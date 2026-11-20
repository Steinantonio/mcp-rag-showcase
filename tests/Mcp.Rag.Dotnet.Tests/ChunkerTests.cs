using Mcp.Rag.Dotnet.Core;

namespace Mcp.Rag.Dotnet.Tests;

public class ChunkerTests
{
    private static Document MakeDoc(string markdown) =>
        new("fixture", "Fixture", [], markdown, "fixture.md");

    [Fact]
    public void Three_sections_yield_three_chunks()
    {
        var doc = MakeDoc("## One\n\n" + new string('a', 40) + "\n\n## Two\n\n" + new string('b', 40) + "\n\n## Three\n\n" + new string('c', 40));
        var chunks = Chunker.ChunkDocument(doc);

        Assert.Equal(3, chunks.Length);
        Assert.Equal("fixture#00", chunks[0].ChunkId);
        Assert.Equal("fixture#01", chunks[1].ChunkId);
        Assert.Equal("fixture#02", chunks[2].ChunkId);
        Assert.Equal("One", chunks[0].Heading);
    }

    [Fact]
    public void No_chunk_exceeds_the_limit()
    {
        var longPara = string.Join(' ', Enumerable.Repeat("word", 600));
        var chunks = Chunker.ChunkDocument(MakeDoc($"## Big\n\n{longPara}"));

        Assert.True(chunks.Length > 1);
        Assert.All(chunks, c => Assert.True(c.Text.Length <= Chunker.MaxChunkChars));
    }

    [Fact]
    public void Content_before_first_heading_gets_empty_heading()
    {
        var chunks = Chunker.ChunkDocument(MakeDoc("intro text\n\n## One\n\nbody"));

        Assert.Equal("", chunks[0].Heading);
        Assert.Equal("intro text", chunks[0].Text);
    }

    [Fact]
    public void Crlf_is_normalized()
    {
        var chunks = Chunker.ChunkDocument(MakeDoc("## One\r\n\r\nbody line\r\n"));

        Assert.Equal("body line", chunks[0].Text);
    }
}
