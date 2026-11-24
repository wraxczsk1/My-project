#include "WarfrontWeatherSubsystem.h"

#include "Components/DirectionalLightComponent.h"
#include "Components/ExponentialHeightFogComponent.h"
#include "Components/SkyAtmosphereComponent.h"
#include "Components/SkyLightComponent.h"
#include "Components/VolumetricCloudComponent.h"
#include "Engine/DirectionalLight.h"
#include "Engine/ExponentialHeightFog.h"
#include "Engine/SkyLight.h"
#include "EngineUtils.h"
#include "Materials/MaterialInterface.h"

namespace
{
    template <typename ActorType>
    bool HasActorOfType(const UWorld& World)
    {
        for (TActorIterator<ActorType> It(&World); It; ++It)
        {
            return true;
        }
        return false;
    }
}

void UWarfrontWeatherSubsystem::OnWorldBeginPlay(UWorld& InWorld)
{
    Super::OnWorldBeginPlay(InWorld);
    if (!InWorld.IsGameWorld())
    {
        return;
    }

    if (!HasActorOfType<ASkyAtmosphere>(InWorld))
    {
        InWorld.SpawnActor<ASkyAtmosphere>();
    }

    if (!HasActorOfType<ADirectionalLight>(InWorld))
    {
        ADirectionalLight* Sun = InWorld.SpawnActor<ADirectionalLight>(
            FVector(0.0f, 0.0f, 50000.0f),
            FRotator(-24.0f, -32.0f, 0.0f));
        if (Sun)
        {
            if (UDirectionalLightComponent* SunComponent =
                    Sun->FindComponentByClass<UDirectionalLightComponent>())
            {
                SunComponent->SetMobility(EComponentMobility::Movable);
                SunComponent->SetIntensity(35000.0f);
                SunComponent->SetLightColor(FLinearColor(1.0f, 0.91f, 0.78f));
                SunComponent->SetAtmosphereSunLight(true);
                SunComponent->SetAtmosphereSunLightIndex(0);
            }
        }
    }

    if (!HasActorOfType<ASkyLight>(InWorld))
    {
        ASkyLight* SkyLight = InWorld.SpawnActor<ASkyLight>();
        if (SkyLight)
        {
            USkyLightComponent* Component = SkyLight->GetLightComponent();
            Component->SetMobility(EComponentMobility::Movable);
            Component->SetIntensity(1.0f);
            Component->RecaptureSky();
        }
    }

    if (!HasActorOfType<AExponentialHeightFog>(InWorld))
    {
        AExponentialHeightFog* Fog = InWorld.SpawnActor<AExponentialHeightFog>();
        if (Fog)
        {
            UExponentialHeightFogComponent* Component = Fog->GetComponent();
            Component->SetFogDensity(0.008f);
            Component->SetFogHeightFalloff(0.18f);
            Component->SetVolumetricFog(true);
        }
    }

    AVolumetricCloud* Clouds = nullptr;
    for (TActorIterator<AVolumetricCloud> It(&InWorld); It; ++It)
    {
        Clouds = *It;
        break;
    }
    if (!Clouds)
    {
        Clouds = InWorld.SpawnActor<AVolumetricCloud>(FVector(0.0f, 0.0f, 180000.0f), FRotator::ZeroRotator);
    }

    UMaterialInterface* CloudMaterial = LoadObject<UMaterialInterface>(
        nullptr,
        TEXT("/Engine/EngineSky/VolumetricClouds/m_SimpleVolumetricCloud_Inst.m_SimpleVolumetricCloud_Inst"));
    if (Clouds && CloudMaterial)
    {
        if (UVolumetricCloudComponent* Component =
                Clouds->FindComponentByClass<UVolumetricCloudComponent>())
        {
            Component->SetMaterial(CloudMaterial);
        }
    }
    else if (!CloudMaterial)
    {
        UE_LOG(LogTemp, Warning, TEXT("Warfront cloud material is unavailable; sky remains cloud-free."));
    }
}
