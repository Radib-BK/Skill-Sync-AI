using Microsoft.EntityFrameworkCore;
using Microsoft.AspNetCore.HttpOverrides;
using ResumeAnalyzer.Api.Data;
using ResumeAnalyzer.Api.Services;

var builder = WebApplication.CreateBuilder(args);

// Configure forwarded headers for Azure deployment
builder.Services.Configure<ForwardedHeadersOptions>(options =>
{
    options.ForwardedHeaders = ForwardedHeaders.XForwardedFor | ForwardedHeaders.XForwardedProto;
    options.KnownNetworks.Clear();
    options.KnownProxies.Clear();
});

// Add services to the container.
builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

// Configure CORS
builder.Services.AddCors(options =>
{
    options.AddPolicy("AllowBlazorClient",
        builder => builder
            .WithOrigins(
                "http://localhost:5000",  // Default Blazor client URL
                "http://localhost:5283",  // API URL
                "https://localhost:7064", // HTTPS API URL
                "http://localhost:5071",  // Current Blazor client URL
                "https://skillsync-resume-api-efhqb2g9gagpfxhh.southeastasia-01.azurewebsites.net" // Azure production URL
            )
            .AllowAnyMethod()
            .AllowAnyHeader());
});

// Configure database
var connectionString = builder.Configuration.GetConnectionString("DefaultConnection");
builder.Services.AddDbContext<ApplicationDbContext>(options =>
{
    options.UseMySql(connectionString, ServerVersion.AutoDetect(connectionString));
    if (builder.Environment.IsDevelopment())
    {
        options.EnableSensitiveDataLogging();
        options.EnableDetailedErrors();
    }
});

// Register services
builder.Services.AddScoped<IFileProcessingService, FileProcessingService>();
builder.Services.AddScoped<IAuthService, AuthService>();
builder.Services.AddHttpClient<IAIServiceClient, AIServiceClient>();

var app = builder.Build();

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseForwardedHeaders();

// Don't use HTTPS redirection in Azure App Service (it's handled by the platform)
if (app.Environment.IsDevelopment())
{
    app.UseHttpsRedirection();
}

app.UseCors("AllowBlazorClient");
app.UseAuthorization();

// Add health check endpoint
app.MapGet("/health", () => Results.Ok(new { 
    status = "healthy", 
    timestamp = DateTime.UtcNow,
    environment = app.Environment.EnvironmentName 
}));

// Add API info endpoint
app.MapGet("/", () => Results.Ok(new { 
    message = "SkillSync Resume Analyzer API", 
    version = "1.0.0",
    environment = app.Environment.EnvironmentName,
    timestamp = DateTime.UtcNow
}));

app.MapControllers();

// Ensure database is created and migrations are applied
if (!app.Environment.IsDevelopment())
{
    try
    {
        using (var scope = app.Services.CreateScope())
        {
            var db = scope.ServiceProvider.GetRequiredService<ApplicationDbContext>();
            var logger = scope.ServiceProvider.GetRequiredService<ILogger<Program>>();
            
            // Check if database can be connected to
            if (db.Database.CanConnect())
            {
                logger.LogInformation("Database connection successful. Applying migrations...");
                db.Database.Migrate();
                logger.LogInformation("Database migrations applied successfully.");
            }
            else
            {
                logger.LogWarning("Cannot connect to database. Skipping migrations.");
            }
        }
    }
    catch (Exception ex)
    {
        // Log the error but don't crash the application
        var logger = app.Services.GetRequiredService<ILogger<Program>>();
        logger.LogError(ex, "Error during database migration. Application will continue without migrations.");
    }
}

app.Run();
