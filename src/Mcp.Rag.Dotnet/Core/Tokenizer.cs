namespace Mcp.Rag.Dotnet.Core;

/// <summary>Tokenization, contract §3. Letter or decimal digit = token character; everything else separates.</summary>
public static class Tokenizer
{
    public static string[] Tokenize(string text)
    {
        if (string.IsNullOrEmpty(text))
            return [];
        var lowered = text.ToLowerInvariant();
        var tokens = new List<string>();
        var current = new System.Text.StringBuilder();

        foreach (var ch in lowered)
        {
            if (char.IsLetterOrDigit(ch))
            {
                current.Append(ch);
            }
            else if (current.Length > 0)
            {
                tokens.Add(current.ToString());
                current.Clear();
            }
        }

        if (current.Length > 0)
            tokens.Add(current.ToString());

        return tokens.ToArray();
    }
}
