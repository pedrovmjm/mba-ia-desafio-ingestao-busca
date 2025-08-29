import os

REQUIRED_ENVS = [
    "GOOGLE_API_KEY",
    "DATABASE_URL",
    "PG_VECTOR_COLLECTION_NAME",
    "PDF_PATH",
]


def validate_envs():
    print("🔍 Validando variáveis de ambiente...")

    found = []
    missing = []

    for env in REQUIRED_ENVS:
        value = os.getenv(env)
        if value:
            # Mascarar API keys para segurança
            if "API_KEY" in env or "PASSWORD" in env:
                masked_value = value[:8] + "..." if len(value) > 8 else "***"
                found.append(f"  ✅ {env} = {masked_value}")
            else:
                found.append(f"  ✅ {env} = {value}")
        else:
            missing.append(f"  ❌ {env}")

    if found:
        print("📋 Variáveis configuradas:")
        for var in found:
            print(var)

    if missing:
        print("\n⚠️  Variáveis ausentes:")
        for var in missing:
            print(var)
        print(f"\n💡 Configure as variáveis ausentes no arquivo .env")
        raise EnvironmentError(
            f"Variáveis de ambiente ausentes: {', '.join([env.replace('  ❌ ', '') for env in missing])}"
        )

    print("✅ Todas as variáveis de ambiente estão configuradas!\n")
    return True
