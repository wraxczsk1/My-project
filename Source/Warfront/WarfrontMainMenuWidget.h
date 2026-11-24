#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "Input/Reply.h"
#include "Styling/SlateBrush.h"
#include "WarfrontMainMenuWidget.generated.h"

class SVerticalBox;
class STextBlock;
class SOverlay;
class UTexture2D;

UCLASS()
class WARFRONT_API UWarfrontMainMenuWidget : public UUserWidget
{
    GENERATED_BODY()

public:
    virtual TSharedRef<SWidget> RebuildWidget() override;
    void ShowLoadingScreen();
    void SetUpdateAvailableVersion(const FString& Version);
    void TogglePauseMenu();
    void ToggleInventory();
    void ShowGameplayHud();
    void SetCombatStatus(int32 Health, int32 MagazineAmmo, int32 ReserveAmmo);
    void BuildMainMenu();

private:
    void BuildMultiplayerScreen();
    void BuildDevLogScreen();
    void BuildPauseMenu();
    void BuildInventoryScreen();
    void BuildSettingsScreen();
    TSharedRef<SWidget> MakeMenuButton(const FText& Label, const FOnClicked& OnClicked) const;

    FReply HandleSinglePlayer();
    FReply HandleMultiplayer();
    FReply HandleDevLog();
    FReply HandleSettings();
    FReply HandleUpdates();
    FReply HandleExit();
    FReply HandleBack();

    TSharedPtr<SVerticalBox> Content;
    TSharedPtr<STextBlock> CombatStatusText;
    TSharedPtr<SBorder> FullscreenBackground;
    TSharedPtr<SBorder> MenuCardBorder;
    TSharedPtr<SBorder> DevLogWindow;
    TSharedPtr<SOverlay> GameplayOverlay;
    FSlateBrush LogoBrush;
    FString UpdateAvailableVersion;

    UPROPERTY(Transient)
    TObjectPtr<UTexture2D> MenuLogo;
};
