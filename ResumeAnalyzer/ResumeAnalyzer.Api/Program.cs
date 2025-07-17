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
app.UseHttpsRedirection();
app.UseCors("AllowBlazorClient");
app.UseAuthorization();
app.MapControllers();

// Ensure database is created and migrations are applied
if (!app.Environment.IsDevelopment())
{
    using (var scope = app.Services.CreateScope())
    {
        var db = scope.ServiceProvider.GetRequiredService<ApplicationDbContext>();
        db.Database.Migrate();
    }
}

app.Run();
