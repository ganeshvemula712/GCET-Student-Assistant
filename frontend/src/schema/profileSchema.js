import { z } from "zod";

export const updateProfileSchema = z.object({
  name: z
    .string()
    .min(3, "Name must be at least 3 characters")
    .max(100, "Name is too long"),
});

export const changePasswordSchema = z
  .object({
    current_password: z
      .string()
      .min(6, "Current password is required"),

    new_password: z
      .string()
      .min(8, "Password must be at least 8 characters"),

    confirm_password: z
      .string()
      .min(8, "Confirm your password"),
  })
  .refine(
    (data) => data.new_password === data.confirm_password,
    {
      path: ["confirm_password"],
      message: "Passwords do not match",
    }
  );