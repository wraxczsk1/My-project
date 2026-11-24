#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "Input/Reply.h"
#include "Styling/SlateBrush.h"
#include "WarfrontMainMenuWidget.generated.h"

class SVerticalBox;
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
    void BuildMainMenu();

private:
    void BuildMultiplayerScreen();
    void BuildDevLogScreen();
    void BuildPauseMenu();
    void BuildInventoryScreen();
    TSharedRef<SWidget> MakeMenuButton(const FText& Label, const FOnClicked& OnClicked) const;

    FReply HandleSinglePlayer();
    FReply HandleMultiplayer();
    FReply HandleDevLog();
    FReply HandleUpdates();
    FReply HandleExit();
    FReply HandleBack();

    TSharedPtr<SVerticalBox> Content;
    FSlateBrush LogoBrush;
    FString UpdateAvailableVersion;

    UPROPERTY(Transient)
    TObjectPtr<UTexture2D> MenuLogo;
};
