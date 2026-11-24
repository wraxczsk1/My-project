#include "WarfrontGameInstance.h"

#include "Blueprint/UserWidget.h"
#include "Engine/World.h"
#include "Engine/GameViewportClient.h"
#include "GameFramework/PlayerController.h"
#include "Kismet/GameplayStatics.h"
#include "Kismet/KismetSystemLibrary.h"
#include "Interfaces/IHttpRequest.h"
#include "Interfaces/IHttpResponse.h"
#include "HttpModule.h"
#include "MoviePlayer.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"
#include "GeneralProjectSettings.h"
#include "WarfrontMainMenuWidget.h"
#include "HAL/PlatformMisc.h"
#include "HAL/PlatformProcess.h"
#include "Misc/MessageDialog.h"
#include "Misc/Paths.h"
#include "Widgets/Layout/SBorder.h"
#include "Widgets/SOverlay.h"
#include "Widgets/Text/STextBlock.h"
#include "Styling/CoreStyle.h"

namespace
{
    bool IsNewerVersion(FString Candidate, FString Current)
    {
        Candidate.RemoveFromStart(TEXT("v"));
        Current.RemoveFromStart(TEXT("v"));

        TArray<FString> CandidateParts;
        TArray<FString> CurrentParts;
        Candidate.ParseIntoArray(CandidateParts, TEXT("."), false);
        Current.ParseIntoArray(CurrentParts, TEXT("."), false);
        if (CandidateParts.Num() == 0 || CurrentParts.Num() == 0)
        {
            return false;
        }

        const int32 PartCount = FMath::Max(CandidateParts.Num(), CurrentParts.Num());
        for (int32 Index = 0; Index < PartCount; ++Index)
        {
            const FString CandidatePart =
                CandidateParts.IsValidIndex(Index) ? CandidateParts[Index] : TEXT("0");
            const FString CurrentPart =
                CurrentParts.IsValidIndex(Index) ? CurrentParts[Index] : TEXT("0");
            if (!CandidatePart.IsNumeric() || !CurrentPart.IsNumeric())
            {
                return false;
            }

            const int32 CandidateValue = FCString::Atoi(*CandidatePart);
            const int32 CurrentValue = FCString::Atoi(*CurrentPart);
            if (CandidateValue != CurrentValue)
            {
                return CandidateValue > CurrentValue;
            }
        }
        return false;
    }
}

void UWarfrontGameInstance::Init()
{
    Super::Init();
    while (GetNumLocalPlayers() > 1)
    {
        RemoveLocalPlayer(GetLocalPlayers().Last());
    }

    if (IsRunningDedicatedServer())
    {
        return;
    }

    if (IGameMoviePlayer* MoviePlayer = GetMoviePlayer())
    {
        FLoadingScreenAttributes LoadingScreen;
        LoadingScreen.bAutoCompleteWhenLoadingCompletes = true;
        LoadingScreen.bWaitForManualStop = false;
        LoadingScreen.MinimumLoadingScreenDisplayTime = 1.0f;
        LoadingScreen.WidgetLoadingScreen =
            SNew(SOverlay)
            + SOverlay::Slot()
            .HAlign(HAlign_Fill)
            .VAlign(VAlign_Fill)
            [
                SNew(SBorder)
                .BorderImage(FCoreStyle::Get().GetBrush("WhiteBrush"))
                .BorderBackgroundColor(FLinearColor(0.025f, 0.035f, 0.045f, 1.0f))
                [
                    SNew(STextBlock)
                    .Text(FText::FromString(TEXT("WARFRONT")))
                    .Font(FCoreStyle::GetDefaultFontStyle(FName(TEXT("Bold")), 48))
                    .ColorAndOpacity(FSlateColor(FLinearColor(0.88f, 0.83f, 0.69f)))
                    .Justification(ETextJustify::Center)
                ]
            ];
        MoviePlayer->SetupLoadingScreen(LoadingScreen);
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("MoviePlayer is unavailable; using the in-game menu only."));
    }
}

void UWarfrontGameInstance::OnStart()
{
    Super::OnStart();
    UGameplayStatics::SetForceDisableSplitscreen(this, true);
    if (UWorld* World = GetWorld())
    {
        if (UGameViewportClient* Viewport = World->GetGameViewport())
        {
            Viewport->SetForceDisableSplitscreen(true);
        }
    }
    while (GetNumLocalPlayers() > 1)
    {
        RemoveLocalPlayer(GetLocalPlayers().Last());
    }
    CheckForUpdates();

    if (UWorld* World = GetWorld())
    {
        World->GetTimerManager().SetTimerForNextTick(
            FTimerDelegate::CreateUObject(this, &UWarfrontGameInstance::ShowMainMenu));
    }
    else
    {
        UE_LOG(LogTemp, Error, TEXT("Warfront could not show its menu because no game world is available."));
    }
}

void UWarfrontGameInstance::CheckForUpdates()
{
    TSharedRef<IHttpRequest, ESPMode::ThreadSafe> Request =
        FHttpModule::Get().CreateRequest();
    Request->SetURL(TEXT("https://api.github.com/repos/wraxczsk1/My-project/releases/latest"));
    Request->SetVerb(TEXT("GET"));
    Request->SetHeader(TEXT("Accept"), TEXT("application/vnd.github+json"));
    Request->SetHeader(TEXT("User-Agent"), TEXT("WarfrontGame"));

    TWeakObjectPtr<UWarfrontGameInstance> WeakThis(this);
    Request->OnProcessRequestComplete().BindLambda(
        [WeakThis](FHttpRequestPtr, FHttpResponsePtr Response, bool bConnectedSuccessfully)
        {
            if (!WeakThis.IsValid())
            {
                return;
            }
            if (!bConnectedSuccessfully || !Response.IsValid())
            {
                UE_LOG(LogTemp, Warning, TEXT("Warfront update check could not reach GitHub."));
                return;
            }
            if (Response->GetResponseCode() != 200)
            {
                UE_LOG(
                    LogTemp,
                    Warning,
                    TEXT("Warfront update check returned HTTP %d."),
                    Response->GetResponseCode());
                return;
            }

            TSharedPtr<FJsonObject> Release;
            const TSharedRef<TJsonReader<>> Reader =
                TJsonReaderFactory<>::Create(Response->GetContentAsString());
            if (!FJsonSerializer::Deserialize(Reader, Release) || !Release.IsValid())
            {
                UE_LOG(LogTemp, Error, TEXT("Warfront could not parse GitHub release information."));
                return;
            }

            FString Tag;
            FString Url;
            if (!Release->TryGetStringField(TEXT("tag_name"), Tag) ||
                !Release->TryGetStringField(TEXT("html_url"), Url))
            {
                UE_LOG(LogTemp, Error, TEXT("GitHub release is missing its tag or URL."));
                return;
            }

            const TArray<TSharedPtr<FJsonValue>>* Assets = nullptr;
            if (!Release->TryGetArrayField(TEXT("assets"), Assets) || !Assets)
            {
                UE_LOG(LogTemp, Error, TEXT("GitHub release is missing its game package."));
                return;
            }

            FString AssetUrl;
            FString Digest;
            for (const TSharedPtr<FJsonValue>& AssetValue : *Assets)
            {
                const TSharedPtr<FJsonObject> Asset = AssetValue->AsObject();
                if (!Asset.IsValid())
                {
                    continue;
                }

                FString AssetName;
                if (Asset->TryGetStringField(TEXT("name"), AssetName) &&
                    AssetName == TEXT("Warfront-Windows.zip"))
                {
                    Asset->TryGetStringField(TEXT("browser_download_url"), AssetUrl);
                    Asset->TryGetStringField(TEXT("digest"), Digest);
                    break;
                }
            }

            if (AssetUrl.IsEmpty())
            {
                UE_LOG(
                    LogTemp,
                    Error,
                    TEXT("GitHub release must include Warfront-Windows.zip."));
                return;
            }

            const FString CurrentVersion =
                GetDefault<UGeneralProjectSettings>()->ProjectVersion;
            if (IsNewerVersion(Tag, CurrentVersion))
            {
                WeakThis->LatestReleaseVersion = Tag;
                WeakThis->LatestReleaseUrl = Url;
                WeakThis->LatestReleaseAssetUrl = AssetUrl;
                WeakThis->LatestReleaseDigest = Digest;
                if (WeakThis->MenuWidget.IsValid())
                {
                    WeakThis->MenuWidget->SetUpdateAvailableVersion(Tag);
                }
                UE_LOG(
                    LogTemp,
                    Display,
                    TEXT("Warfront update %s is available."),
                    *Tag);
            }
            else
            {
                UE_LOG(
                    LogTemp,
                    Display,
                    TEXT("Warfront is up to date (version %s)."),
                    *CurrentVersion);
            }
        });

    if (!Request->ProcessRequest())
    {
        UE_LOG(LogTemp, Error, TEXT("Warfront could not start the GitHub update request."));
    }
}

void UWarfrontGameInstance::Shutdown()
{
    if (UWorld* World = GetWorld())
    {
        World->GetTimerManager().ClearTimer(LoadingTimer);
    }

    Super::Shutdown();
}

void UWarfrontGameInstance::ShowMainMenu()
{
    UWorld* World = GetWorld();
    if (!World || !World->IsGameWorld())
    {
        return;
    }

    if (!MenuWidget.IsValid())
    {
        MenuWidget = CreateWidget<UWarfrontMainMenuWidget>(this, UWarfrontMainMenuWidget::StaticClass());
    }

    if (!MenuWidget.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("Warfront failed to create the main menu widget."));
        return;
    }

    MenuWidget->AddToViewport(100);
    if (!LatestReleaseVersion.IsEmpty())
    {
        MenuWidget->SetUpdateAvailableVersion(LatestReleaseVersion);
    }

    if (APlayerController* PlayerController = GetFirstLocalPlayerController())
    {
        PlayerController->SetShowMouseCursor(true);
        PlayerController->SetIgnoreMoveInput(true);
        PlayerController->SetIgnoreLookInput(true);

        FInputModeUIOnly InputMode;
        InputMode.SetWidgetToFocus(MenuWidget->TakeWidget());
        InputMode.SetLockMouseToViewportBehavior(EMouseLockMode::DoNotLock);
        PlayerController->SetInputMode(InputMode);
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Main menu is visible, but no local player controller was available."));
    }
}

void UWarfrontGameInstance::BeginSinglePlayer()
{
    if (MenuWidget.IsValid())
    {
        MenuWidget->ShowLoadingScreen();
    }

    UWorld* World = GetWorld();
    if (!World)
    {
        UE_LOG(LogTemp, Error, TEXT("Cannot start single player because no game world is available."));
        return;
    }

    UGameplayStatics::OpenLevel(
        this,
        FName(TEXT("/Game/Maps/WarfrontMap.WarfrontMap")),
        true);

    World->GetTimerManager().SetTimer(
        LoadingTimer,
        FTimerDelegate::CreateUObject(this, &UWarfrontGameInstance::FinishLoading),
        1.0f,
        false);

    UE_LOG(LogTemp, Display, TEXT("Warfront singleplayer is starting; loading the active battlefield."));
}

void UWarfrontGameInstance::FinishLoading()
{
    if (MenuWidget.IsValid())
    {
        MenuWidget->ShowGameplayHud();
    }

    if (APlayerController* PlayerController = GetFirstLocalPlayerController())
    {
        PlayerController->SetIgnoreMoveInput(false);
        PlayerController->SetIgnoreLookInput(false);
        PlayerController->SetShowMouseCursor(false);
        PlayerController->SetInputMode(FInputModeGameOnly());
    }
}

void UWarfrontGameInstance::TogglePauseMenu()
{
    if (!MenuWidget.IsValid())
    {
        ShowMainMenu();
    }
    if (MenuWidget.IsValid())
    {
        MenuWidget->TogglePauseMenu();
    }
}

void UWarfrontGameInstance::ToggleInventory()
{
    if (bInventoryOpen)
    {
        bInventoryOpen = false;
        ResumeGame();
        return;
    }

    if (MenuWidget.IsValid())
    {
        bInventoryOpen = true;
        MenuWidget->ToggleInventory();
    }
}

void UWarfrontGameInstance::ResumeGame()
{
    bInventoryOpen = false;
    if (MenuWidget.IsValid())
    {
        MenuWidget->ShowGameplayHud();
    }
    if (APlayerController* PlayerController = GetFirstLocalPlayerController())
    {
        PlayerController->SetIgnoreMoveInput(false);
        PlayerController->SetIgnoreLookInput(false);
        PlayerController->SetShowMouseCursor(false);
        PlayerController->SetInputMode(FInputModeGameOnly());
    }
}

void UWarfrontGameInstance::UpdateCombatStatus(
    int32 Health,
    int32 MagazineAmmo,
    int32 ReserveAmmo)
{
    if (MenuWidget.IsValid())
    {
        MenuWidget->SetCombatStatus(Health, MagazineAmmo, ReserveAmmo);
    }
}

void UWarfrontGameInstance::ReturnToMainMenu()
{
    if (MenuWidget.IsValid())
    {
        MenuWidget->BuildMainMenu();
    }
    if (APlayerController* PlayerController = GetFirstLocalPlayerController())
    {
        PlayerController->SetShowMouseCursor(true);
        PlayerController->SetIgnoreMoveInput(true);
        PlayerController->SetIgnoreLookInput(true);
        FInputModeUIOnly InputMode;
        InputMode.SetWidgetToFocus(MenuWidget->TakeWidget());
        PlayerController->SetInputMode(InputMode);
    }
}

void UWarfrontGameInstance::QuitGame()
{
    UKismetSystemLibrary::QuitGame(
        this,
        GetFirstLocalPlayerController(),
        EQuitPreference::Quit,
        false);
}

void UWarfrontGameInstance::OpenReleasesPage()
{
    if (LatestReleaseAssetUrl.IsEmpty())
    {
        FMessageDialog::Open(
            EAppMsgType::Ok,
            FText::FromString(TEXT("Aktualizace zatim neni dostupna. Zkus to pozdeji.")));
        return;
    }

    const EAppReturnType::Type Choice = FMessageDialog::Open(
        EAppMsgType::YesNo,
        FText::FromString(
            FString::Printf(
                TEXT("Je dostupna verze %s. Stahnout a nainstalovat aktualizaci?"),
                *LatestReleaseVersion)));
    if (Choice == EAppReturnType::Yes)
    {
        InstallLatestUpdate();
    }
}

void UWarfrontGameInstance::InstallLatestUpdate()
{
    const FString ExecutablePath = FPlatformProcess::ExecutablePath();
    const FString InstallDirectory = FPaths::GetPath(ExecutablePath);
    const FString UpdaterPath = FPaths::Combine(InstallDirectory, TEXT("WarfrontUpdater.ps1"));
    if (!FPaths::FileExists(UpdaterPath))
    {
        UE_LOG(LogTemp, Error, TEXT("WarfrontUpdater.ps1 was not staged beside the game executable."));
        FMessageDialog::Open(
            EAppMsgType::Ok,
            FText::FromString(TEXT("Aktualizacni soubor ve slozce hry chybi.")));
        return;
    }

    const FString Parameters = FString::Printf(
        TEXT("-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File \"%s\" ")
        TEXT("-DownloadUrl \"%s\" -ExpectedDigest \"%s\" -ProcessId %u ")
        TEXT("-InstallDirectory \"%s\" -ExecutablePath \"%s\""),
        *UpdaterPath,
        *LatestReleaseAssetUrl,
        *LatestReleaseDigest,
        FPlatformProcess::GetCurrentProcessId(),
        *InstallDirectory,
        *ExecutablePath);
    FProcHandle UpdaterProcess = FPlatformProcess::CreateProc(
        TEXT("powershell.exe"),
        *Parameters,
        false,
        true,
        true,
        nullptr,
        0,
        *InstallDirectory,
        nullptr);
    if (!UpdaterProcess.IsValid())
    {
        UE_LOG(LogTemp, Error, TEXT("Could not start the Warfront updater process."));
        return;
    }

    FPlatformMisc::RequestExit(false);
}
