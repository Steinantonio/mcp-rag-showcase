namespace Mcp.Rag.Dotnet.Core;

/// <summary>BM25 scoring, contract §4. Constants are contract, not tuning knobs.</summary>
public sealed class Bm25Index
{
    private const double K1 = 1.2;
    private const double B = 0.75;

    private readonly Entry[] _entries;
    private readonly Dictionary<string, int> _documentFrequency;
    private readonly double _avgLength;

    public Bm25Index(Chunk[] chunks)
    {
        _entries = chunks.Select(chunk =>
        {
            var tokens = Tokenizer.Tokenize(chunk.Text);
            var freq = new Dictionary<string, int>();
            foreach (var token in tokens)
                freq[token] = freq.GetValueOrDefault(token) + 1;
            return new Entry(chunk, freq, tokens.Length);
        }).ToArray();

        _documentFrequency = new Dictionary<string, int>();
        foreach (var entry in _entries)
        {
            foreach (var term in entry.TermFrequency.Keys)
                _documentFrequency[term] = _documentFrequency.GetValueOrDefault(term) + 1;
        }

        _avgLength = _entries.Length > 0
            ? (double)_entries.Sum(e => e.Length) / _entries.Length
            : 0.0;
    }

    public int ChunkCount => _entries.Length;
    public int TotalTokens => _entries.Sum(e => e.Length);
    public double AvgChunkTokens => _avgLength;

    public ScoredChunk[] Score(string query)
    {
        var tokens = Tokenizer.Tokenize(query);
        if (tokens.Length == 0 || _entries.Length == 0)
            return [];

        var scored = new List<ScoredChunk>();
        var count = _entries.Length;
        var avgLength = _avgLength;

        foreach (var entry in _entries)
        {
            var score = 0.0;
            foreach (var term in tokens)
            {
                if (!entry.TermFrequency.TryGetValue(term, out var freq) || freq == 0)
                    continue;

                var docFreq = _documentFrequency[term];
                var idf = Math.Log(1 + (count - docFreq + 0.5) / (docFreq + 0.5));
                score += idf * (freq * (K1 + 1)) /
                         (freq + K1 * (1 - B + B * entry.Length / avgLength));
            }

            if (score > 0)
                scored.Add(new ScoredChunk(entry.Chunk, score));
        }

        scored.Sort((a, b) =>
        {
            var cmp = b.Score.CompareTo(a.Score);
            if (cmp != 0) return cmp;
            cmp = string.CompareOrdinal(a.Chunk.DocId, b.Chunk.DocId);
            if (cmp != 0) return cmp;
            return string.CompareOrdinal(a.Chunk.ChunkId, b.Chunk.ChunkId);
        });

        return scored.ToArray();
    }

    private sealed record Entry(Chunk Chunk, Dictionary<string, int> TermFrequency, int Length);
}
