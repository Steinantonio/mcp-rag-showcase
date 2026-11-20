using Mcp.Rag.Dotnet.Core;

namespace Mcp.Rag.Dotnet.Tests;

public class TokenizerTests
{
    [Fact]
    public void Contract_example_matches_spec()
    {
        var tokens = Tokenizer.Tokenize("Rotate the API key! (v2)");
        Assert.Equal(["rotate", "the", "api", "key", "v2"], tokens);
    }

    [Fact]
    public void Punctuation_and_underscore_separate_tokens()
    {
        var tokens = Tokenizer.Tokenize("snake_case-name.v2");
        Assert.Equal(["snake", "case", "name", "v2"], tokens);
    }

    [Fact]
    public void Empty_and_separator_only_return_empty()
    {
        Assert.Empty(Tokenizer.Tokenize(""));
        Assert.Empty(Tokenizer.Tokenize("   !!! --- ... "));
    }

    [Fact]
    public void Digits_and_letters_are_kept()
    {
        var tokens = Tokenizer.Tokenize("sev1");
        Assert.Equal(["sev1"], tokens);
    }

    [Fact]
    public void No_stemming_or_stopwords()
    {
        var tokens = Tokenizer.Tokenize("rotating rotation rotated the of");
        Assert.Equal(["rotating", "rotation", "rotated", "the", "of"], tokens);
    }
}
