/** Retro CRT shader and color palette rasterizer manager. */

export interface ShaderConfig {
  scanlines: boolean;
  scanlineIntensity: number; // 0 to 100
  phosphorGlow: boolean;
  crtCurvature: boolean;
  vhsNoise: boolean;
  palette: "default" | "ega16" | "vga256" | "c64" | "amber_monochrome" | "green_monochrome";
  resolutionScaling: "native" | "320x240" | "480x360" | "640x480";
}

class RetroShaderService {
  private config: ShaderConfig = {
    scanlines: true,
    scanlineIntensity: 12,
    phosphorGlow: true,
    crtCurvature: false,
    vhsNoise: false,
    palette: "default",
    resolutionScaling: "native",
  };

  public getConfig(): ShaderConfig {
    return { ...this.config };
  }

  public updateConfig(newConfig: Partial<ShaderConfig>): void {
    this.config = { ...this.config, ...newConfig };
    this.applyToDOM();
    this.saveToStorage();
  }

  public init(): void {
    const saved = localStorage.getItem("openprevue_shader_config");
    if (saved) {
      try {
        this.config = { ...this.config, ...JSON.parse(saved) };
      } catch {
        // Fallback to default
      }
    }
    this.applyToDOM();
  }

  private saveToStorage(): void {
    try {
      localStorage.setItem("openprevue_shader_config", JSON.stringify(this.config));
    } catch {
      // Ignore
    }
  }

  public applyToDOM(): void {
    const root = document.documentElement;
    const body = document.body;

    // Apply Palette Classes
    const palettes = ["palette-ega16", "palette-vga256", "palette-c64", "palette-amber", "palette-green"];
    palettes.forEach((p) => body.classList.remove(p));

    if (this.config.palette === "ega16") body.classList.add("palette-ega16");
    else if (this.config.palette === "vga256") body.classList.add("palette-vga256");
    else if (this.config.palette === "c64") body.classList.add("palette-c64");
    else if (this.config.palette === "amber_monochrome") body.classList.add("palette-amber");
    else if (this.config.palette === "green_monochrome") body.classList.add("palette-green");

    // Scanline Intensity CSS Variable
    root.style.setProperty("--scanline-opacity", (this.config.scanlineIntensity / 100).toString());

    // Curvature class
    if (this.config.crtCurvature) {
      body.classList.add("crt-curvature-active");
    } else {
      body.classList.remove("crt-curvature-active");
    }

    // Phosphor bloom
    if (this.config.phosphorGlow) {
      body.classList.add("phosphor-bloom-active");
    } else {
      body.classList.remove("phosphor-bloom-active");
    }

    // Low-res resolution downscaling container
    const appEl = document.getElementById("app");
    if (appEl) {
      appEl.classList.remove("res-320x240", "res-480x360", "res-640x480");
      if (this.config.resolutionScaling === "320x240") appEl.classList.add("res-320x240");
      else if (this.config.resolutionScaling === "480x360") appEl.classList.add("res-480x360");
      else if (this.config.resolutionScaling === "640x480") appEl.classList.add("res-640x480");
    }
  }
}

export const retroShader = new RetroShaderService();
