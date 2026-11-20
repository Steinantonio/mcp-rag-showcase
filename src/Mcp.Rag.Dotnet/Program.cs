using System.Text.Json;
using Mcp.Rag.Dotnet.Adapters;
using Mcp.Rag.Dotnet.Core;
using Microsoft.AspNetCore.Builder;
using Microsoft.AspNetCore.Hosting;
using Microsoft.AspNetCore.Http;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;

// Modes: --cli (parity), --http (container / smoke), default (MCP over stdio).

if (args.Length > 0 && args[0] == "--cli")
    return RunCli(args[1..]);

if (args.Length > 0 && args[0] == "--http")
    return await RunHttp(args[1..]);

return await RunStdio(args);

static async Task<int> RunHttp(string[] httpArgs)
{
    var port = 8081;
    for (var i = 0; i < httpArgs.Length; i++)
        if (httpArgs[i] == "--port" && i + 1 < httpArgs.Length) port = int.Parse(httpArgs[i + 1]);

    var loadResult = CorpusSource.Load(FindCorpusDir());
    if (loadResult is not Result<Document[]>.Ok okDocs)
    {
        Console.Error.WriteLine($"fatal {loadResult.RagError.Code}: {loadResult.RagError.Message}");
        return 1;
    }

    var engine = new RagEngine(okDocs.Value);

    var builder = WebApplication.CreateBuilder();
    builder.WebHost.UseUrls($"http://0.0.0.0:{port}");
    builder.Services.AddSingleton(engine);
    builder.Services.AddMcpServer()
        .WithHttpTransport()
        .WithTools<RagMcpTools>();

    var app = builder.Build();

    app.MapGet("/health", () =>
    {
        var stats = engine.Stats();
        return Results.Json(new
        {
            status = "ok",
            implementation = "dotnet",
            contractVersion = 1,
            corpus = new
            {
                documents = stats.Documents,
                chunks = stats.Chunks,
                tokens = stats.Tokens,
                avgChunkTokens = stats.AvgChunkTokens,
            },
        });
    });

    app.MapMcp("/mcp");

    await app.RunAsync();
    return 0;
}

static async Task<int> RunStdio(string[] serverArgs)
{
    var loadResult = CorpusSource.Load(FindCorpusDir());
    if (loadResult is not Result<Document[]>.Ok okDocs)
    {
        Console.Error.WriteLine($"fatal {loadResult.RagError.Code}: {loadResult.RagError.Message}");
        return 1;
    }

    var builder = Host.CreateApplicationBuilder(serverArgs);
    builder.Services.AddSingleton(new RagEngine(okDocs.Value));
    builder.Services.AddMcpServer()
        .WithStdioServerTransport()
        .WithTools<RagMcpTools>();

    var host = builder.Build();
    await host.RunAsync();
    return 0;
}

static int RunCli(string[] cliArgs)
{
    if (cliArgs.Length < 2)
    {
        Console.Error.WriteLine("usage: --cli <query|answer|ingest> <text> [-k N] [--json]");
        return 2;
    }

    var loadResult = CorpusSource.Load(FindCorpusDir());
    if (loadResult is not Result<Document[]>.Ok okDocs)
    {
        Console.Error.WriteLine($"fatal {loadResult.RagError.Code}: {loadResult.RagError.Message}");
        return 1;
    }

    var engine = new RagEngine(okDocs.Value);
    var command = cliArgs[0];

    if (command == "ingest")
    {
        var stats = engine.Stats();
        Console.WriteLine($"{stats.Documents} documents, {stats.Chunks} chunks, avgdl {stats.AvgChunkTokens}");
        return 0;
    }

    var query = cliArgs[1];
    var k = command == "answer" ? 3 : 5;
    var json = false;

    for (var i = 2; i < cliArgs.Length; i++)
    {
        if (cliArgs[i] == "-k" && i + 1 < cliArgs.Length) k = int.Parse(cliArgs[i + 1]);
        if (cliArgs[i] == "--json") json = true;
    }

    if (command == "query")
    {
        var result = engine.Search(query, k);
        if (!result.IsOk) { Console.Error.WriteLine($"error {result.RagError.Code}: {result.RagError.Message}"); return 2; }
        var value = result.Unwrap();
        if (json)
        {
            Console.WriteLine(JsonSerializer.Serialize(new
            {
                query = value.Query,
                k = value.K,
                totalMatched = value.TotalMatched,
                results = value.Results.Select(r => new
                {
                    docId = r.DocId, chunkId = r.ChunkId, title = r.Title, heading = r.Heading,
                    score = r.Score, citation = r.Citation, text = r.Text,
                }),
            }));
        }
        else
        {
            Console.WriteLine($"query: {value.Query}  (matched {value.TotalMatched})");
            for (var i = 0; i < value.Results.Length; i++)
                Console.WriteLine($"{i + 1}. {value.Results[i].ChunkId}  {value.Results[i].Score:F4}  {value.Results[i].Heading}");
        }
        return 0;
    }

    if (command == "answer")
    {
        var result = engine.Answer(query, k);
        if (!result.IsOk) { Console.Error.WriteLine($"error {result.RagError.Code}: {result.RagError.Message}"); return 2; }
        var value = result.Unwrap();
        if (json)
            Console.WriteLine(JsonSerializer.Serialize(new { query = value.Query, answer = value.Text, citations = value.Citations, grounded = value.Grounded }));
        else
        {
            Console.WriteLine(value.Text);
            if (value.Citations.Length > 0) Console.WriteLine($"\nsources: {string.Join(", ", value.Citations)}");
        }
        return 0;
    }

    Console.Error.WriteLine($"unknown command: {command}");
    return 2;
}

static string FindCorpusDir()
{
    var env = Environment.GetEnvironmentVariable("MCP_RAG_CORPUS");
    if (!string.IsNullOrWhiteSpace(env)) return env;
    var candidate = Path.Combine(AppContext.BaseDirectory, "..", "..", "..", "..", "corpus");
    return Directory.Exists(candidate) ? Path.GetFullPath(candidate) : "corpus";
}
