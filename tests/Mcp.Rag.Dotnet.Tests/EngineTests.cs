using System.Text.Json;
using Mcp.Rag.Dotnet.Adapters;
using Mcp.Rag.Dotnet.Core;

namespace Mcp.Rag.Dotnet.Tests;

public class EngineTests : IDisposable
{
    private readonly RagEngine _engine = default!;
    private readonly GoldenCase[] _golden;

    public EngineTests()
    {
        var repoRoot = FindRepoRoot();
        var corpusDir = Path.Combine(repoRoot, "corpus");
        var loadResult = CorpusSource.Load(corpusDir);

        if (loadResult is Result<Document[]>.Ok okDocs)
        {
            _engine = new RagEngine(okDocs.Value);
        }
        else
        {
            Assert.Fail(loadResult.RagError.Message);
            throw new InvalidOperationException("unreachable");
        }

        var goldenPath = Path.Combine(corpusDir, "golden", "queries.json");
        var goldenJson = JsonDocument.Parse(File.ReadAllText(goldenPath));
        _golden = goldenJson.RootElement.GetProperty("cases")
            .EnumerateArray()
            .Select(c => new GoldenCase(
                c.GetProperty("id").GetString()!,
                c.GetProperty("query").GetString()!,
                c.GetProperty("k").GetInt32(),
                c.GetProperty("expectDocIds").EnumerateArray().Select(e => e.GetString()!).ToArray(),
                c.GetProperty("expectGrounded").GetBoolean()
            ))
            .ToArray();
    }

    public void Dispose() { }

    private static string FindRepoRoot()
    {
        var dir = AppContext.BaseDirectory;
        while (dir != null && !Directory.Exists(Path.Combine(dir, "corpus")))
            dir = Path.GetDirectoryName(dir);
        return dir!;
    }

    private sealed record GoldenCase(string Id, string Query, int K, string[] ExpectDocIds, bool ExpectGrounded);

    [Fact]
    public void All_ten_golden_cases_are_present() => Assert.Equal(10, _golden.Length);

    [Fact]
    public void Golden_search_cases_match()
    {
        var failures = new List<string>();
        foreach (var g in _golden)
        {
            var result = _engine.Search(g.Query, g.K);
            if (!result.IsOk) Assert.Fail(result.RagError.Message);
            var actual = ((Result<SearchResult>.Ok)result).Value.Results.Select(r => r.DocId).ToArray();
            if (!actual.SequenceEqual(g.ExpectDocIds))
                failures.Add($"{g.Id}: expected [{string.Join(", ", g.ExpectDocIds)}], got [{string.Join(", ", actual)}]");
        }
        if (failures.Count > 0) Assert.Fail(string.Join("\n", failures));
    }

    [Fact]
    public void Golden_grounded_flags_match()
    {
        foreach (var g in _golden)
        {
            var result = _engine.Answer(g.Query, Math.Min(g.K, 10));
            if (!result.IsOk) Assert.Fail(result.RagError.Message);
            Assert.Equal(g.ExpectGrounded, ((Result<Answer>.Ok)result).Value.Grounded);
        }
    }

    [Fact]
    public void Search_with_no_match_returns_nothing()
    {
        var result = _engine.Search("kubernetes helm chart", 5);
        Assert.True(result.IsOk);
        Assert.Equal(0, ((Result<SearchResult>.Ok)result).Value.TotalMatched);
    }

    [Fact]
    public void Unknown_document_is_an_error()
    {
        var result = _engine.GetDocument("does-not-exist");
        Assert.False(result.IsOk);
        Assert.Equal(ErrorCode.DOC_NOT_FOUND, result.RagError.Code);
    }

    [Fact]
    public void Answer_is_extractive()
    {
        var result = _engine.Answer("how do I rotate an api key", 3);
        Assert.True(result.IsOk);
        var answer = result.Unwrap();
        Assert.True(answer.Grounded);
        Assert.NotEmpty(answer.Citations);

        // Collect all cited chunk texts.
        var citedTexts = new List<string>();
        foreach (var citation in answer.Citations)
        {
            var parts = citation.Split('#');
            var docId = parts[0];
            var docResult = _engine.GetDocument(docId);
            Assert.True(docResult.IsOk);
            var doc = docResult.Unwrap();
            var chunks = Chunker.ChunkDocument(doc);
            var chunk = chunks.First(c => c.ChunkId == citation);
            citedTexts.Add(chunk.Text);
        }

        var allText = string.Join(' ', citedTexts);
        var sentences = System.Text.RegularExpressions.Regex
            .Split(answer.Text, @"(?<=[.!?])\s+")
            .Where(s => s.Trim().Length > 0);

        foreach (var sentence in sentences)
            Assert.Contains(sentence, allText);
    }

    [Fact]
    public void Invalid_arguments_are_rejected()
    {
        Assert.False(_engine.Search("", 5).IsOk);
        Assert.False(_engine.Search("   ", 5).IsOk);
        Assert.False(_engine.Search("alpha", 0).IsOk);
        Assert.False(_engine.Search("alpha", 21).IsOk);
        Assert.False(_engine.Answer("alpha", 11).IsOk);
    }

    [Fact]
    public void Stats_reflect_the_engine()
    {
        var stats = _engine.Stats();
        Assert.Equal(15, stats.Documents);
        Assert.Equal(63, stats.Chunks);
        Assert.True(stats.Tokens > 0);
    }
}
