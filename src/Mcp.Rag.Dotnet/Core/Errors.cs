namespace Mcp.Rag.Dotnet.Core;

public enum ErrorCode { INVALID_ARGUMENT, DOC_NOT_FOUND, CORPUS_UNAVAILABLE, INTERNAL }

public sealed record RagError(ErrorCode Code, string Message);

public abstract record Result<T>
{
    private Result() { }

    public sealed record Ok(T Value) : Result<T>;
    public sealed record Err(RagError error) : Result<T>;

    public bool IsOk => this is Ok;
    public T Unwrap() => this is Ok ok ? ok.Value : throw new InvalidOperationException(RagError.Message);
    public RagError RagError => this is Err err ? err.error
        : throw new InvalidOperationException("Result is Ok, not Err");

    public static Result<T> Success(T value) => new Ok(value);
    public static Result<T> Failure(RagError error) => new Err(error);
}

public static class Errors
{
    public static Result<T> InvalidArgument<T>(string message) =>
        Result<T>.Failure(new RagError(ErrorCode.INVALID_ARGUMENT, message));

    public static Result<T> DocNotFound<T>(string docId) =>
        Result<T>.Failure(new RagError(ErrorCode.DOC_NOT_FOUND, $"document not found: {docId}"));
}
