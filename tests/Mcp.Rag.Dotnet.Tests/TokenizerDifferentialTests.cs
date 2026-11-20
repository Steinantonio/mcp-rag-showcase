using System.Text.Json;
using Mcp.Rag.Dotnet.Core;

namespace Mcp.Rag.Dotnet.Tests;

public class TokenizerDifferentialTests
{
    private static readonly ExpectedCase[] ExpectedCases = LoadExpected();

    private static ExpectedCase[] LoadExpected()
    {
        var repoRoot = FindRepoRoot();
        var path = Path.Combine(repoRoot, "tests", "fixtures", "tokenizer_expected.json");
        return JsonSerializer.Deserialize<ExpectedCase[]>(File.ReadAllText(path))!;
    }

    private static string FindRepoRoot()
    {
        var dir = AppContext.BaseDirectory;
        while (dir != null && !Directory.Exists(Path.Combine(dir, "corpus")))
            dir = Path.GetDirectoryName(dir);
        return dir ?? throw new DirectoryNotFoundException("Cannot find repository root");
    }

    private sealed record ExpectedCase(string Input, string[] Tokens);

    [Fact]
    public void All_200_cases_are_present() => Assert.Equal(200, ExpectedCases.Length);

    [Fact]
    public void Every_case_matches_the_python_tokenizer_output()
    {
        var failures = new List<string>();
        foreach (var entry in ExpectedCases)
        {
            var actual = Tokenizer.Tokenize(entry.Input);
            if (!actual.SequenceEqual(entry.Tokens))
                failures.Add($"{entry.Input}\n  expected: [{string.Join(", ", entry.Tokens)}]\n  actual:   [{string.Join(", ", actual)}]");
        }

        if (failures.Count > 0)
            Assert.Fail(string.Join("\n\n", failures.Take(5)));
    }
}
