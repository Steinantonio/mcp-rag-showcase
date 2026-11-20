namespace Mcp.Rag.Dotnet.Core;

/// <summary>Chunking, contract §1-2. Split on H2, pack to 1200 chars, no overlap.</summary>
public static class Chunker
{
    public const int MaxChunkChars = 1200;
    private const string HeadingPrefix = "## ";

    public static Chunk[] ChunkDocument(Document document)
    {
        var body = Normalize(document.Markdown);
        var sections = SplitSections(body);
        var chunks = new List<Chunk>();

        foreach (var (heading, text) in sections)
        {
            foreach (var piece in SplitLong(text))
            {
                chunks.Add(new Chunk(
                    DocId: document.DocId,
                    ChunkId: $"{document.DocId}#{chunks.Count:D2}",
                    Title: document.Title,
                    Heading: heading,
                    Text: piece
                ));
            }
        }

        return chunks.ToArray();
    }

    private static string Normalize(string body)
    {
        var text = body.Replace("\r\n", "\n").Replace("\r", "\n");
        var lines = text.Split('\n');
        for (var i = 0; i < lines.Length; i++)
            lines[i] = lines[i].TrimEnd();
        return string.Join('\n', lines).TrimEnd('\n');
    }

    private static List<(string Heading, string Text)> SplitSections(string body)
    {
        var sections = new List<(string, string)>();
        var heading = "";
        var buffer = new List<string>();

        void Flush()
        {
            var text = string.Join('\n', buffer).Trim();
            if (text.Length > 0)
                sections.Add((heading, text));
            buffer.Clear();
        }

        foreach (var line in body.Split('\n'))
        {
            if (line.StartsWith(HeadingPrefix))
            {
                Flush();
                heading = line[HeadingPrefix.Length..].Trim();
            }
            else
            {
                buffer.Add(line);
            }
        }

        Flush();
        return sections;
    }

    private static string[] SplitLong(string text)
    {
        var pieces = new List<string>();
        var current = "";

        foreach (var paragraph in text.Split("\n\n", StringSplitOptions.None))
        {
            if (paragraph.Length > MaxChunkChars)
            {
                if (current.Length > 0)
                {
                    pieces.Add(current);
                    current = "";
                }

                var rest = paragraph;
                while (rest.Length > MaxChunkChars)
                {
                    var cut = rest.LastIndexOf(' ', MaxChunkChars);
                    if (cut <= 0) cut = MaxChunkChars;
                    pieces.Add(rest[..cut]);
                    rest = rest[cut..].TrimStart();
                }

                if (rest.Length > 0)
                    current = rest;
                continue;
            }

            var candidate = current.Length > 0 ? $"{current}\n\n{paragraph}" : paragraph;
            if (candidate.Length > MaxChunkChars)
            {
                pieces.Add(current);
                current = paragraph;
            }
            else
            {
                current = candidate;
            }
        }

        if (current.Length > 0)
            pieces.Add(current);

        return pieces.ToArray();
    }
}
