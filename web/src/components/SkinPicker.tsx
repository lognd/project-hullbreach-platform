import { useState } from "react";
import { ApiError } from "@/api/auth";
import { equipSkin, unequipSkin, type OwnedSkin } from "@/api/me";
import { Notice } from "@/components/Notice";

type SkinPickerProps = {
  token: string;
  skins: OwnedSkin[];
  initial: OwnedSkin | null;
};

// frob:ticket 01M2H5T117A35Q8AA9THRZTTYB
// frob:ticket 01M5XYWVF56BWJXQ43EBP9FP8F
// frob:doc docs/index.md#equipped-skin
/** Lists the owned skins as toggle buttons; pressing one equips it (PUT /api/v1/me/equipped), pressing the equipped one again unequips it (DELETE), and a refusal shows as an alert. */
export function SkinPicker({ token, skins, initial }: SkinPickerProps) {
  const [equippedId, setEquippedId] = useState<string | null>(initial?.id ?? null);
  const [pending, setPending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function choose(skin: OwnedSkin): Promise<void> {
    setPending(true);
    setError(null);
    try {
      if (skin.id === equippedId) {
        await unequipSkin(token);
        setEquippedId(null);
      } else {
        const saved = await equipSkin(token, skin.id);
        setEquippedId(saved.id);
      }
    } catch (caught: unknown) {
      setError(
        caught instanceof ApiError ? caught.detail : "Something went wrong. Please try again.",
      );
    } finally {
      setPending(false);
    }
  }

  return (
    <>
      {error === null ? null : (
        <Notice tone="error" role="alert">
          <span>{error}</span>
        </Notice>
      )}
      <ul className="flex flex-wrap gap-space-8">
        {skins.map((skin) => {
          const active = skin.id === equippedId;
          return (
            <li key={skin.id}>
              <button
                type="button"
                aria-pressed={active}
                disabled={pending}
                onClick={() => void choose(skin)}
                className={`wrap-anywhere border px-space-12 py-space-8 text-font-size-14 disabled:opacity-50 ${
                  active ? "border-signal bg-panel" : "border-line bg-panel hover:border-ink"
                }`}
              >
                {skin.name}
                {active ? " (equipped)" : ""}
              </button>
            </li>
          );
        })}
      </ul>
    </>
  );
}
