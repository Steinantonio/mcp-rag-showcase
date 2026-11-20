using System.Text.RegularExpressions;
using Mcp.Rag.Dotnet.Core;

namespace Mcp.Rag.Dotnet.Adapters;

/// <summary>Filesystem corpus source with restricted front matter parsing. Mirrors corpus_fs.py.</summary>
public static partial class CorpusSource
{
    [GeneratedRegex(@"^[a-z0-9]+(-[a-z0-9]+)*$")]
    private static partial Regex DocIdPattern();

    public static Result<Document[]> Load(string corpusDir)
    {
        if (!Directory.Exists(corpusDir))
            return Result<Document[]>.Failure(new RagError(
                ErrorCode.CORPUS_UNAVAILABLE, $"directory not found: {corpusDir}"));

        try
        {
            var files = Directory.GetFiles(corpusDir, "*.md")
                .Where(f => !string.Equals(Path.GetFileName(f), "README.md", StringComparison.OrdinalIgnoreCase))
                .OrderBy(f => f, StringComparer.OrdinalIgnoreCase)
                .ToArray();

            var documents = files.Select(ParseDocument).ToArray();

            var ids = documents.Select(d => d.DocId).ToArray();
            if (ids.Distinct().Count() != ids.Length)
                return Result<Document[]>.Failure(new RagError(
                    ErrorCode.CORPUS_UNAVAILABLE, "duplicate document ids"));

            return Result<Document[]>.Success(documents);
        }
        catch (Exception ex) when (ex is IOException or FormatException)
        {
            return Result<Document[]>.Failure(new RagError(ErrorCode.CORPUS_UNAVAILABLE, ex.Message));
        }
    }

    private static Document ParseDocument(string path)
    {
        var raw = File.ReadAllText(path);
        var text = raw.Replace("\r\n", "\n").Replace("\r", "\n");
        var lines = text.Split('\n');

        if (lines.Length == 0 || lines[0].Trim() != "---")
            throw new FormatException($"{path}: missing front matter");

        var end = Array.IndexOf(lines, "---", 1);
        if (end < 0)
            throw new FormatException($"{path}: unterminated front matter");

        var meta = new Dictionary<string, string>();
        for (var i = 1; i < end; i++)
        {
            var colon = lines[i].IndexOf(':');
            if (colon < 0) continue;
            var key = lines[i][..colon].Trim();
            if (key is "id" or "title" or "tags")
                meta[key] = lines[i][(colon + 1)..].Trim();
        }

        var docId = meta.GetValueOrDefault("id", "");
        if (string.IsNullOrEmpty(docId) || !DocIdPattern().IsMatch(docId))
            throw new FormatException($"{path}: invalid or missing id");

        var tags = meta.GetValueOrDefault("tags", "")
            .Split(',', StringSplitOptions.RemoveEmptyEntries | StringSplitOptions.TrimEntries)
            .Select(t => t.ToLowerInvariant())
            .ToArray();

        var markdown = string.Join('\n', lines[(end + 1)..]);
        var title = meta.GetValueOrDefault("title", docId);

        return new Document(docId, title, tags, markdown, path);
    }
}
