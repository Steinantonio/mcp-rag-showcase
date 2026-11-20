using Mcp.Rag.Dotnet.Core;

namespace Mcp.Rag.Dotnet.Tests;

public class Bm25Tests
{
    private static Chunk C(string docId, int idx, string text) =>
        new(docId, $"{docId}#{idx:D2}", docId, "", text);

    [Fact]
    public void Single_term_score_is_ln_two_when_tf_one_and_dl_equals_avgdl()
    {
        var index = new Bm25Index([C("a", 0, "alpha beta"), C("b", 0, "gamma delta")]);
        var scored = index.Score("alpha");

        Assert.Single(scored);
        Assert.Equal(Math.Log(2), scored[0].Score, 12);
    }

    [Fact]
    public void Chunks_without_term_are_excluded()
    {
        var index = new Bm25Index([C("a", 0, "alpha beta"), C("b", 0, "gamma delta")]);
        Assert.Empty(index.Score("omega"));
    }

    [Fact]
    public void Ties_break_on_doc_id_then_chunk_id()
    {
        var index = new Bm25Index([
            C("zulu", 0, "alpha"),
            C("alpha", 1, "alpha"),
            C("alpha", 0, "alpha"),
        ]);

        var scored = index.Score("alpha");
        Assert.Equal(["alpha#00", "alpha#01", "zulu#00"], scored.Select(s => s.Chunk.ChunkId));
    }

    [Fact]
    public void Repeated_query_tokens_count_repeatedly()
    {
        var index = new Bm25Index([C("a", 0, "alpha beta"), C("b", 0, "gamma delta")]);

        var once = index.Score("alpha")[0].Score;
        var twice = index.Score("alpha alpha")[0].Score;

        Assert.Equal(once * 2, twice, 12);
    }

    [Fact]
    public void Empty_index_scores_nothing() =>
        Assert.Empty(new Bm25Index([]).Score("alpha"));
}
