namespace Mcp.Rag.Dotnet.Core;

/// <summary>Immutable values, no behavior. Mirrors mcp_rag_py.core.model.</summary>

public sealed record Document(string DocId, string Title, string[] Tags, string Markdown, string Source);

public sealed record Chunk(string DocId, string ChunkId, string Title, string Heading, string Text);

public sealed record ScoredChunk(Chunk Chunk, double Score);

public sealed record SearchHit(
    string DocId,
    string ChunkId,
    string Title,
    string Heading,
    double Score,
    string Citation,
    string Text
);

public sealed record SearchResult(string Query, int K, int TotalMatched, SearchHit[] Results);

public sealed record Answer(string Query, string Text, string[] Citations, bool Grounded);

public sealed record CorpusStats(int Documents, int Chunks, int Tokens, double AvgChunkTokens);
