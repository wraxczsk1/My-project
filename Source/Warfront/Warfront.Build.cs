using UnrealBuildTool;

public class Warfront : ModuleRules
{
    public Warfront(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

        PublicDependencyModuleNames.AddRange(
            new string[]
            {
                "Core",
                "CoreUObject",
                "Engine",
                "InputCore",
                "UMG",
                "Slate",
                "SlateCore",
                "MoviePlayer",
                "EngineSettings",
                "HTTP",
                "Json"
            });
    }
}
