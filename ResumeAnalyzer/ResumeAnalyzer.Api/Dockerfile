FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS base
WORKDIR /app
EXPOSE 80
EXPOSE 443

FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY ["ResumeAnalyzer.Api/ResumeAnalyzer.Api.csproj", "ResumeAnalyzer.Api/"]
COPY ["ResumeAnalyzer.Shared/ResumeAnalyzer.Shared.csproj", "ResumeAnalyzer.Shared/"]
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