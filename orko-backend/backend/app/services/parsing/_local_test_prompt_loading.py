from backend.app.services.parsing.parser_engine import (
    load_domain_prompt,
    get_prompt_version,
)

if __name__ == "__main__":
    text = load_domain_prompt("trading")
    version, updated_at = get_prompt_version("trading")

    print("Prompt version:", version, "updated_at:", updated_at)
    print("\n--- Prompt Preview (first 300 chars) ---")
    print(text[:300])
