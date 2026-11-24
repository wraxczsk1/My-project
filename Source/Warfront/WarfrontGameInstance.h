#pragma once

#include "CoreMinimal.h"
#include "Engine/GameInstance.h"
#include "TimerManager.h"
#include "WarfrontGameInstance.generated.h"

class UWarfrontMainMenuWidget;

UCLASS()
class WARFRONT_API UWarfrontGameInstance : public UGameInstance
{
    GENERATED_BODY()

public:
    virtual void Init() override;
    virtual void OnStart() override;
    virtual void Shutdown() override;

    void BeginSinglePlayer();
    void QuitGame();
    void OpenReleasesPage();
    void TogglePauseMenu();
    void ToggleInventory();
    void ResumeGame();
    void ReturnToMainMenu();

private:
    void ShowMainMenu();
    void FinishLoading();
    void CheckForUpdates();
    void InstallLatestUpdate();

    TWeakObjectPtr<UWarfrontMainMenuWidget> MenuWidget;
    FTimerHandle LoadingTimer;
    FString LatestReleaseUrl;
    FString LatestReleaseVersion;
    FString LatestReleaseAssetUrl;
    FString LatestReleaseDigest;
};
