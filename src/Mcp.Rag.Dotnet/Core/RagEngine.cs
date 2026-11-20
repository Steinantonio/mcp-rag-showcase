using System.Text.RegularExpressions;

namespace Mcp.Rag.Dotnet.Core;

/// <summary>The engine: three use cases over the index, contract §5. Pure, no I/O.</summary>
public partial class RagEngine
{
    private const int MaxQueryChars = 512;
    private const int MaxKSearch = 20;
    private const int MaxKAnswer = 10;
    private const int MaxAnswerSentences = 3;
    private const int MinSentenceChars = 20;
    private const string NoMatchAnswer = "No content in the corpus matches this question.";

    private readonly Dictionary<string, Document> _documents;
    private readonly Bm25Index _index;

    [GeneratedRegex(@"(?<=[.!?])\s+")]
    private static partial Regex SentenceBreak();

    public RagEngine(Document[] documents)
    {
        _documents = documents.ToDictionary(d => d.DocId);
        var chunks = documents.SelectMany(Chunker.ChunkDocument).ToArray();
        _index = new Bm25Index(chunks);
    }

    public Chunk[] Chunks => _index.GetType().GetProperty("Chunks") is null
        ? []
        : []; // Chunks are internal to the index; engine exposes via stats only. The adapter computes chunkCount.

    public int ChunkCountFor(string docId) =>
        Chunker.ChunkDocument(_documents[docId]).Length;

    public CorpusStats Stats() =>
        new(_documents.Count, _index.ChunkCount, _index.TotalTokens, Math.Round(_index.AvgChunkTokens, 2));

    public Result<SearchResult> Search(string query, int k = 5)
    {
        var error = Validate(query, k, MaxKSearch);
        if (error is not null) return Result<SearchResult>.Failure(error);

        var ranked = _index.Score(query);
        return Result<SearchResult>.Success(new SearchResult(
            Query: query,
            K: k,
            TotalMatched: ranked.Length,
            Results: ranked.Take(k).Select(ToHit).ToArray()
        ));
    }

    public Result<Document> GetDocument(string docId)
    {
        if (!_documents.TryGetValue(docId, out var document))
            return Errors.DocNotFound<Document>(docId);
        return Result<Document>.Success(document);
    }

    public Result<Answer> Answer(string query, int k = 3)
    {
        var error = Validate(query, k, MaxKAnswer);
        if (error is not null) return Result<Answer>.Failure(error);

        var ranked = _index.Score(query);
        if (ranked.Length == 0)
            return Result<Answer>.Success(new Answer(query, NoMatchAnswer, [], false));

        var queryTerms = new HashSet<string>(Tokenizer.Tokenize(query));
        var candidates = new List<(int Overlap, int Rank, int Position, string Sentence, string ChunkId)>();

        for (var rank = 0; rank < Math.Min(ranked.Length, k); rank++)
        {
            var sentences = SentenceBreak().Split(ranked[rank].Chunk.Text)
                .Select(s => s.Trim())
                .Where(s => s.Length >= MinSentenceChars)
                .ToArray();

            for (var pos = 0; pos < sentences.Length; pos++)
            {
                var sentenceTokens = new HashSet<string>(Tokenizer.Tokenize(sentences[pos]));
                var overlap = queryTerms.Count(t => sentenceTokens.Contains(t));
                if (overlap > 0)
                    candidates.Add((overlap, rank, pos, sentences[pos], ranked[rank].Chunk.ChunkId));
            }
        }

        if (candidates.Count == 0)
        {
            var fallback = SentenceBreak().Split(ranked[0].Chunk.Text)
                .Select(s => s.Trim())
                .Where(s => s.Length >= MinSentenceChars)
                .Take(MaxAnswerSentences)
                .ToArray();

            return fallback.Length == 0
                ? Result<Answer>.Success(new Answer(query, NoMatchAnswer, [], false))
                : Result<Answer>.Success(new Answer(query, string.Join(' ', fallback), [ranked[0].Chunk.ChunkId], true));
        }

        candidates.Sort((a, b) =>
        {
            var cmp = b.Overlap.CompareTo(a.Overlap);
            if (cmp != 0) return cmp;
            cmp = a.Rank.CompareTo(b.Rank);
            if (cmp != 0) return cmp;
            return a.Position.CompareTo(b.Position);
        });

        var selected = candidates.Take(MaxAnswerSentences).ToList();
        selected.Sort((a, b) =>
        {
            var cmp = a.Rank.CompareTo(b.Rank);
            return cmp != 0 ? cmp : a.Position.CompareTo(b.Position);
        });

        var citations = new List<string>();
        foreach (var (_, _, _, _, chunkId) in selected)
        {
            if (!citations.Contains(chunkId))
                citations.Add(chunkId);
        }

        return Result<Answer>.Success(new Answer(
            query,
            string.Join(' ', selected.Select(s => s.Sentence)),
            citations.ToArray(),
            true
        ));
    }

    private static RagError? Validate(string query, int k, int maxK)
    {
        if (string.IsNullOrWhiteSpace(query))
            return new RagError(ErrorCode.INVALID_ARGUMENT, "query must not be empty");
        if (query.Length > MaxQueryChars)
            return new RagError(ErrorCode.INVALID_ARGUMENT, $"query must be at most {MaxQueryChars} characters");
        if (k < 1 || k > maxK)
            return new RagError(ErrorCode.INVALID_ARGUMENT, $"k must be between 1 and {maxK}");
        return null;
    }

    private static SearchHit ToHit(ScoredChunk scored) => new(
        DocId: scored.Chunk.DocId,
        ChunkId: scored.Chunk.ChunkId,
        Title: scored.Chunk.Title,
        Heading: scored.Chunk.Heading,
        Score: Math.Round(scored.Score, 4),
        Citation: scored.Chunk.ChunkId,
        Text: scored.Chunk.Text
    );
}
