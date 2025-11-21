import type { ChangeEvent } from "react";
import type { HyperParamField } from "@/api/types";
import Input from "@/components/ui/Input";
import Select from "@/components/ui/Select";
import Tooltip from "@/components/ui/Tooltip";

type Props = {
  fields: HyperParamField[];
  values: Record<string, unknown>;
  onChange: (key: string, value: unknown) => void;
};

const HyperparamForm = ({ fields, values, onChange }: Props) => {
  const renderField = (field: HyperParamField) => {
    const value = values[field.key] ?? field.default ?? "";
    const label = (
      <div style={{ display: "flex", alignItems: "center", gap: "0.25rem" }}>
        <span>{field.label}</span>
        {field.info && (
          <Tooltip label={field.info}>
            <span style={{ cursor: "help", color: "var(--color-text-secondary)" }}>ⓘ</span>
          </Tooltip>
        )}
      </div>
    );

    if (field.options?.length) {
      return (
        <label key={field.key} className="grid" style={{ gap: "0.4rem" }}>
          {label}
          <Select
            value={String(value)}
            onChange={(event: ChangeEvent<HTMLSelectElement>) =>
              onChange(field.key, event.target.value)
            }
          >
            {field.options.map((option) => (
              <option key={String(option)} value={String(option)}>
                {String(option)}
              </option>
            ))}
          </Select>
        </label>
      );
    }

    const inputType = field.type.includes("float") ? "number" : "number";
    const isList = field.type.endsWith("_list");

    return (
      <label key={field.key} className="grid" style={{ gap: "0.4rem" }}>
        {label}
        <Input
          type={isList ? "text" : inputType}
          value={
            isList
              ? (Array.isArray(value) ? value.join(", ") : value ?? "").toString()
              : String(value ?? "")
          }
          min={field.min}
          max={field.max}
          step={field.type.includes("float") ? "0.01" : "1"}
          onChange={(event: ChangeEvent<HTMLInputElement>) => {
            const val = event.target.value;
            if (isList) {
              onChange(
                field.key,
                val
                  .split(",")
                  .map((item: string) => item.trim())
                  .filter(Boolean)
                  .map((item: string) =>
                    field.type.startsWith("float") ? Number(item) : Number(item),
                  ),
              );
            } else if (field.type.startsWith("float")) {
              onChange(field.key, Number(val));
            } else if (field.type.startsWith("int")) {
              onChange(field.key, Number(val));
            } else {
              onChange(field.key, val);
            }
          }}
        />
      </label>
    );
  };

  return (
    <div className="grid" style={{ gap: "1rem" }}>
      {fields.map((field) => renderField(field))}
    </div>
  );
};

export default HyperparamForm;


