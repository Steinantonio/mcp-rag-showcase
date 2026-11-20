using Mcp.Rag.Dotnet.Core;
using ModelContextProtocol.Server;

namespace Mcp.Rag.Dotnet.Adapters;

public sealed class RagMcpTools(RagEngine engine)
{
    [McpServerTool]
    public SearchResult Search(string query, int k = 5)
    {
        var result = engine.Search(query, k);
        if (result is Result<SearchResult>.Ok ok) return ok.Value;
        throw new InvalidOperationException(result.RagError.Message);
    }

    [McpServerTool]
    public Document GetDocument(string docId)
    {
        var result = engine.GetDocument(docId);
        if (result is Result<Document>.Ok ok) return ok.Value;
        throw new InvalidOperationException(result.RagError.Message);
    }

    [McpServerTool]
    public Answer Answer(string query, int k = 3)
    {
        var result = engine.Answer(query, k);
        if (result is Result<Answer>.Ok ok) return ok.Value;
        throw new InvalidOperationException(result.RagError.Message);
    }
}
