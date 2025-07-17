# Free Deployment Guide for SkillSync AI

## Recommended Free Deployment Stack

### 1. Frontend Deployment (GitHub Pages)
```bash
# 1. Add base href to index.html
<base href="/SkillSync-AI/"/>

# 2. Create GitHub Actions workflow
name: Deploy to GitHub Pages
on:
  push:
    branches: [ main ]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Setup .NET
      uses: actions/setup-dotnet@v1
      with:
        dotnet-version: '8.0.x'
    - name: Publish
      run: dotnet publish ResumeAnalyzer.Client/ResumeAnalyzer.Client.csproj -c Release -o release --nologo
    - name: Deploy
      uses: JamesIves/github-pages-deploy-action@v4
      with:
        branch: gh-pages
        folder: release/wwwroot
```

### 2. Backend API (Railway.app)
1. Create Railway account
2. Connect GitHub repository
3. Add environment variables:
```env
ASPNETCORE_ENVIRONMENT=Production
ConnectionStrings__DefaultConnection=your_mysql_connection_string
JWT__Secret=your_secret_key
```
4. Add Dockerfile to API project:
```dockerfile
FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS base
WORKDIR /app
EXPOSE 80

FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY ["ResumeAnalyzer.Api/ResumeAnalyzer.Api.csproj", "ResumeAnalyzer.Api/"]
RUN dotnet restore "ResumeAnalyzer.Api/ResumeAnalyzer.Api.csproj"
COPY . .
WORKDIR "/src/ResumeAnalyzer.Api"
RUN dotnet build "ResumeAnalyzer.Api.csproj" -c Release -o /app/build

FROM build AS publish
RUN dotnet publish "ResumeAnalyzer.Api.csproj" -c Release -o /app/publish

FROM base AS final
WORKDIR /app
COPY --from=publish /app/publish .
ENTRYPOINT ["dotnet", "ResumeAnalyzer.Api.dll"]
```

### 3. Database (PlanetScale)
1. Create free PlanetScale account
2. Create new database
3. Get connection string
4. Update in Railway environment variables

### 4. AI Service (Hugging Face Spaces)
1. Create Hugging Face account
2. Create new Space with FastAPI template
3. Upload AI service code
4. Add requirements.txt
5. Configure environment variables:
```env
HF_SPACE=your_space_name
MODEL_CACHE_DIR=/tmp/models
```

## Configuration Updates

### 1. Update API URLs in Client
```csharp
// Program.cs
builder.Services.AddScoped(sp => new HttpClient 
{ 
    BaseAddress = new Uri("https://your-railway-app.railway.app/") 
});
```

### 2. Update CORS in API
```csharp
// Program.cs
app.UseCors(x => x
    .AllowAnyMethod()
    .AllowAnyHeader()
    .WithOrigins("https://yourusername.github.io")
);
```

### 3. Update AI Service URL in API
```csharp
// appsettings.json
{
  "AIService": {
    "BaseUrl": "https://your-huggingface-space.hf.space"
  }
}
```

## Deployment Steps

1. **Database**:
   ```bash
   # Run migrations
   dotnet ef database update
   ```

2. **Backend**:
   ```bash
   # Railway will auto-deploy on push
   git push origin main
   ```

3. **Frontend**:
   ```bash
   # GitHub Actions will auto-deploy
   git push origin main
   ```

4. **AI Service**:
   ```bash
   # Hugging Face will auto-deploy on push
   git push huggingface main
   ```

## Free Tier Limitations

- **GitHub Pages**: 1GB storage, 100GB bandwidth/month
- **Railway**: 500 hours/month
- **PlanetScale**: 5GB storage, 1B rows read/month
- **Hugging Face Spaces**: Basic CPU runtime

## Monitoring

- Use Railway's built-in monitoring
- PlanetScale's database metrics
- GitHub Pages deployment status
- Hugging Face Spaces logs

## Cost Optimization

1. Use model caching in AI service
2. Implement client-side caching
3. Use connection pooling for database
4. Optimize API responses with compression

## Backup Strategy

1. Regular GitHub backups
2. PlanetScale automatic backups
3. Export analysis history periodically
4. Cache AI model weights locally

Remember to never commit sensitive information like connection strings or API keys. Use environment variables or secret management services. 