using NetArchTest.Rules;

namespace Mcp.Rag.Dotnet.Tests;

public class ArchitectureTests
{
    [Fact]
    public void Core_does_not_reference_MCP_or_ASP_NET()
    {
        var result = Types.InAssembly(typeof(Mcp.Rag.Dotnet.Core.RagEngine).Assembly)
            .That().ResideInNamespace("Mcp.Rag.Dotnet.Core")
            .ShouldNot().HaveDependencyOnAny(
                "ModelContextProtocol",
                "Microsoft.AspNetCore",
                "FastAPI",  // not .NET but harmless to check
                "System.IO"
            )
            .GetResult();

        Assert.True(result.IsSuccessful, string.Join("\n", result.FailingTypeNames ?? []));
    }

    [Fact]
    public void Adapters_do_not_depend_on_each_other_in_the_wrong_direction()
    {
        var result = Types.InAssembly(typeof(Mcp.Rag.Dotnet.Adapters.RagMcpTools).Assembly)
            .That().ResideInNamespace("Mcp.Rag.Dotnet.Adapters")
            .ShouldNot().HaveDependencyOnAny(
                "Mcp.Rag.Dotnet.Apps"  // adapters don't depend on composition roots
            )
            .GetResult();

        Assert.True(result.IsSuccessful, string.Join("\n", result.FailingTypeNames ?? []));
    }
}
