#include "WarfrontMainMenuWidget.h"

#include "Engine/Texture2D.h"
#include "Engine/World.h"
#include "Styling/CoreStyle.h"
#include "WarfrontGameInstance.h"
#include "Widgets/Input/SButton.h"
#include "Widgets/Layout/SBox.h"
#include "Widgets/Layout/SBorder.h"
#include "Widgets/SOverlay.h"
#include "Widgets/SBoxPanel.h"
#include "Widgets/Images/SImage.h"
#include "Widgets/SBoxPanel.h"
#include "Widgets/Text/STextBlock.h"

TSharedRef<SWidget> UWarfrontMainMenuWidget::RebuildWidget()
{
    MenuLogo = LoadObject<UTexture2D>(
        nullptr,
        TEXT("/Game/Warfront/UI/GUI/WarfrontLogo.WarfrontLogo"));
    if (MenuLogo)
    {
        LogoBrush.SetResourceObject(MenuLogo);
        LogoBrush.ImageSize = FVector2D(460.0f, 230.0f);
    }

    Content = SNew(SVerticalBox);
    BuildMainMenu();

    return SNew(SOverlay)
        + SOverlay::Slot()
        .HAlign(HAlign_Fill)
        .VAlign(VAlign_Fill)
        [
            SNew(SBorder)
            .BorderImage(FCoreStyle::Get().GetBrush("WhiteBrush"))
            .BorderBackgroundColor(FLinearColor(0.018f, 0.026f, 0.032f, 0.94f))
        ]
        + SOverlay::Slot()
        .HAlign(HAlign_Center)
        .VAlign(VAlign_Center)
        [
            SNew(SBorder)
            .BorderImage(FCoreStyle::Get().GetBrush("WhiteBrush"))
            .BorderBackgroundColor(FLinearColor(0.052f, 0.074f, 0.082f, 0.98f))
            .Padding(FMargin(38.0f))
            [
                SNew(SBox)
                .WidthOverride(620.0f)
                [
                    Content.ToSharedRef()
                ]
            ]
        ];
}

void UWarfrontMainMenuWidget::BuildMainMenu()
{
    Content->ClearChildren();

    if (MenuLogo)
    {
        Content->AddSlot()
            .AutoHeight()
            .HAlign(HAlign_Center)
            .Padding(0.0f, 0.0f, 0.0f, 14.0f)
            [
                SNew(SImage)
                .Image(&LogoBrush)
            ];
    }

    Content->AddSlot()
        .AutoHeight()
        .HAlign(HAlign_Center)
        .Padding(0.0f, 0.0f, 0.0f, 8.0f)
        [
            SNew(STextBlock)
            .Text(FText::FromString(TEXT("WARFRONT")))
            .Font(FCoreStyle::GetDefaultFontStyle(FName(TEXT("Bold")), 42))
            .ColorAndOpacity(FSlateColor(FLinearColor(0.88f, 0.83f, 0.69f)))
            .Justification(ETextJustify::Center)
        ];

    Content->AddSlot()
        .AutoHeight()
        .HAlign(HAlign_Center)
        .Padding(0.0f, 0.0f, 0.0f, 22.0f)
        [
            SNew(STextBlock)
        .Text(FText::FromString(TEXT("HRA SE SLOVNIM BOJISTEM")))
            .Font(FCoreStyle::GetDefaultFontStyle(FName(TEXT("Regular")), 16))
        .ColorAndOpacity(FSlateColor(FLinearColor(0.64f, 0.72f, 0.70f)))
            .Justification(ETextJustify::Center)
        ];

    Content->AddSlot()
        .AutoHeight()
        .Padding(0.0f, 5.0f)
        [
            MakeMenuButton(
                FText::FromString(TEXT("SINGLEPLAYER")),
                FOnClicked::CreateUObject(this, &UWarfrontMainMenuWidget::HandleSinglePlayer))
        ];

    Content->AddSlot()
        .AutoHeight()
        .Padding(0.0f, 5.0f)
        [
            MakeMenuButton(
                FText::FromString(TEXT("MULTIPLAYER")),
                FOnClicked::CreateUObject(this, &UWarfrontMainMenuWidget::HandleMultiplayer))
        ];

    Content->AddSlot()
        .AutoHeight()
        .Padding(0.0f, 5.0f)
        [
            MakeMenuButton(
                FText::FromString(TEXT("DEV-LOG")),
                FOnClicked::CreateUObject(this, &UWarfrontMainMenuWidget::HandleDevLog))
        ];

    Content->AddSlot()
        .AutoHeight()
        .Padding(0.0f, 5.0f)
        [
            MakeMenuButton(
                UpdateAvailableVersion.IsEmpty()
                    ? FText::FromString(TEXT("ZKONTROLOVAT AKTUALIZACE"))
                    : FText::FromString(FString(TEXT("AKTUALIZACE ")) + UpdateAvailableVersion),
                FOnClicked::CreateUObject(this, &UWarfrontMainMenuWidget::HandleUpdates))
        ];

    Content->AddSlot()
        .AutoHeight()
        .Padding(0.0f, 5.0f)
        [
            MakeMenuButton(
                FText::FromString(TEXT("KONEC HRY")),
                FOnClicked::CreateUObject(this, &UWarfrontMainMenuWidget::HandleExit))
        ];
}

void UWarfrontMainMenuWidget::TogglePauseMenu()
{
    BuildPauseMenu();
    if (UWorld* World = GetWorld())
    {
        if (APlayerController* PlayerController =
                World->GetFirstPlayerController())
        {
            PlayerController->SetShowMouseCursor(true);
            PlayerController->SetIgnoreMoveInput(true);
            PlayerController->SetIgnoreLookInput(true);

            FInputModeUIOnly InputMode;
            InputMode.SetWidgetToFocus(TakeWidget());
            InputMode.SetLockMouseToViewportBehavior(EMouseLockMode::DoNotLock);
            PlayerController->SetInputMode(InputMode);
        }
    }
}

void UWarfrontMainMenuWidget::ToggleInventory()
{
    BuildInventoryScreen();
    if (UWorld* World = GetWorld())
    {
        if (APlayerController* PlayerController =
                World->GetFirstPlayerController())
        {
            PlayerController->SetShowMouseCursor(true);
            PlayerController->SetIgnoreMoveInput(true);
            PlayerController->SetIgnoreLookInput(true);
            FInputModeUIOnly InputMode;
            InputMode.SetWidgetToFocus(TakeWidget());
            PlayerController->SetInputMode(InputMode);
        }
    }
}

void UWarfrontMainMenuWidget::ShowGameplayHud()
{
    Content->ClearChildren();
    CombatStatusText = SNew(STextBlock)
        .Text(FText::FromString(TEXT("ZDRAVI 100  |  CZ 805 BREN  30 / 120")))
        .Font(FCoreStyle::GetDefaultFontStyle(FName(TEXT("Bold")), 18))
        .ColorAndOpacity(FSlateColor(FLinearColor(0.88f, 0.90f, 0.86f, 0.95f)));

    Content->AddSlot()
        .FillHeight(1.0f)
        .HAlign(HAlign_Left)
        .VAlign(VAlign_Bottom)
        .Padding(28.0f, 0.0f, 0.0f, 24.0f)
        [
            CombatStatusText.ToSharedRef()
        ];

    Content->AddSlot()
        .FillHeight(1.0f)
        .HAlign(HAlign_Center)
        .VAlign(VAlign_Center)
        [
            SNew(STextBlock)
            .Text(FText::FromString(TEXT("+")))
            .Font(FCoreStyle::GetDefaultFontStyle(FName(TEXT("Bold")), 24))
            .ColorAndOpacity(FSlateColor(FLinearColor(0.88f, 0.90f, 0.86f, 0.9f)))
        ];
}

void UWarfrontMainMenuWidget::SetCombatStatus(
    int32 Health,
    int32 MagazineAmmo,
    int32 ReserveAmmo)
{
    if (CombatStatusText.IsValid())
    {
        CombatStatusText->SetText(FText::FromString(
            FString::Printf(
                TEXT("ZDRAVI %d  |  CZ 805 BREN  %d / %d"),
                Health,
                MagazineAmmo,
                ReserveAmmo)));
    }
}

void UWarfrontMainMenuWidget::BuildPauseMenu()
{
    Content->ClearChildren();
    Content->AddSlot()
        .AutoHeight()
        .HAlign(HAlign_Center)
        .Padding(0.0f, 0.0f, 0.0f, 18.0f)
        [
            SNew(STextBlock)
            .Text(FText::FromString(TEXT("PAUSE")))
            .Font(FCoreStyle::GetDefaultFontStyle(FName(TEXT("Bold")), 38))
            .ColorAndOpacity(FSlateColor(FLinearColor(0.88f, 0.83f, 0.69f)))
        ];

    Content->AddSlot().AutoHeight().Padding(0.0f, 5.0f)
        [
            MakeMenuButton(
                FText::FromString(TEXT("ZPET DO HRY")),
                FOnClicked::CreateLambda([this]()
                {
                    if (UWorld* World = GetWorld())
                    {
                        if (UWarfrontGameInstance* GameInstance =
                                Cast<UWarfrontGameInstance>(World->GetGameInstance()))
                        {
                            GameInstance->ResumeGame();
                        }
                    }
                    return FReply::Handled();
                }))
        ];

    Content->AddSlot().AutoHeight().Padding(0.0f, 5.0f)
        [
            MakeMenuButton(
                FText::FromString(TEXT("INVENTAR")),
                FOnClicked::CreateLambda([this]()
                {
                    BuildInventoryScreen();
                    return FReply::Handled();
                }))
        ];

    Content->AddSlot().AutoHeight().Padding(0.0f, 5.0f)
        [
            MakeMenuButton(
                FText::FromString(TEXT("ZPET DO HLAVNIHO MENU")),
                FOnClicked::CreateLambda([this]()
                {
                    if (UWorld* World = GetWorld())
                    {
                        if (UWarfrontGameInstance* GameInstance =
                                Cast<UWarfrontGameInstance>(World->GetGameInstance()))
                        {
                            GameInstance->ReturnToMainMenu();
                        }
                    }
                    return FReply::Handled();
                }))
        ];
}

void UWarfrontMainMenuWidget::BuildInventoryScreen()
{
    Content->ClearChildren();
    Content->AddSlot()
        .AutoHeight()
        .HAlign(HAlign_Center)
        .Padding(0.0f, 0.0f, 0.0f, 16.0f)
        [
            SNew(STextBlock)
            .Text(FText::FromString(TEXT("INVENTAR")))
            .Font(FCoreStyle::GetDefaultFontStyle(FName(TEXT("Bold")), 38))
            .ColorAndOpacity(FSlateColor(FLinearColor(0.88f, 0.83f, 0.69f)))
        ];

    Content->AddSlot()
        .AutoHeight()
        .Padding(0.0f, 4.0f)
        [
            SNew(STextBlock)
            .Text(FText::FromString(
                TEXT("PRIMARNI: CZ 805 BREN\nSEKUNDARNI: CZ P-10 C\n")
                TEXT("HELM: MICH / flecktarn\nVESTA: PLATE CARRIER\n")
                TEXT("VYBAVA: bandáže, granát, optika")))
            .Font(FCoreStyle::GetDefaultFontStyle(FName(TEXT("Regular")), 16))
            .ColorAndOpacity(FSlateColor(FLinearColor(0.78f, 0.82f, 0.79f)))
            .AutoWrapText(true)
        ];

    Content->AddSlot().AutoHeight().Padding(0.0f, 12.0f)
        [
            MakeMenuButton(
                FText::FromString(TEXT("ZAVRIT INVENTAR")),
                FOnClicked::CreateLambda([this]()
                {
                    if (UWorld* World = GetWorld())
                    {
                        if (UWarfrontGameInstance* GameInstance =
                                Cast<UWarfrontGameInstance>(World->GetGameInstance()))
                        {
                            GameInstance->ResumeGame();
                        }
                    }
                    return FReply::Handled();
                }))
        ];
}

void UWarfrontMainMenuWidget::BuildMultiplayerScreen()
{
    Content->ClearChildren();

    Content->AddSlot()
        .AutoHeight()
        .HAlign(HAlign_Center)
        .Padding(0.0f, 0.0f, 0.0f, 18.0f)
        [
            SNew(STextBlock)
            .Text(FText::FromString(TEXT("MULTIPLAYER")))
            .Font(FCoreStyle::GetDefaultFontStyle(FName(TEXT("Bold")), 36))
            .ColorAndOpacity(FSlateColor(FLinearColor(0.88f, 0.83f, 0.69f)))
            .Justification(ETextJustify::Center)
        ];

    Content->AddSlot()
        .AutoHeight()
        .HAlign(HAlign_Center)
        .Padding(0.0f, 0.0f, 0.0f, 28.0f)
        [
            SNew(STextBlock)
            .Text(FText::FromString(TEXT("Online pripojeni zatim neni nakonfigurovano.")))
            .Font(FCoreStyle::GetDefaultFontStyle(FName(TEXT("Regular")), 16))
            .ColorAndOpacity(FSlateColor(FLinearColor(0.72f, 0.76f, 0.73f)))
            .Justification(ETextJustify::Center)
        ];

    Content->AddSlot()
        .AutoHeight()
        [
            MakeMenuButton(
                FText::FromString(TEXT("ZPET DO MENU")),
                FOnClicked::CreateUObject(this, &UWarfrontMainMenuWidget::HandleBack))
        ];
}

void UWarfrontMainMenuWidget::BuildDevLogScreen()
{
    Content->ClearChildren();

    Content->AddSlot()
        .AutoHeight()
        .HAlign(HAlign_Center)
        .Padding(0.0f, 0.0f, 0.0f, 20.0f)
        [
            SNew(STextBlock)
            .Text(FText::FromString(TEXT("DEV-LOG")))
            .Font(FCoreStyle::GetDefaultFontStyle(FName(TEXT("Bold")), 36))
            .ColorAndOpacity(FSlateColor(FLinearColor(0.88f, 0.83f, 0.69f)))
            .Justification(ETextJustify::Center)
        ];

    Content->AddSlot()
        .AutoHeight()
        .Padding(0.0f, 0.0f, 0.0f, 24.0f)
        [
            SNew(STextBlock)
            .Text(FText::FromString(
                TEXT("0.1.0 - Proceduralni bojiste s lesy, mesty, cestami a nerovnym terenem.\n")
                TEXT("Pridano volumetricke oblaky, atmosferu, slunce a mlhu.\n")
                TEXT("Pridano hlavni menu, uvodni nacitani a hratelny singleplayer.\n")
                TEXT("Multiplayer zatim neni dostupny.")))
            .Font(FCoreStyle::GetDefaultFontStyle(FName(TEXT("Regular")), 16))
            .ColorAndOpacity(FSlateColor(FLinearColor(0.72f, 0.76f, 0.73f)))
            .AutoWrapText(true)
        ];

    Content->AddSlot()
        .AutoHeight()
        [
            MakeMenuButton(
                FText::FromString(TEXT("ZPET DO MENU")),
                FOnClicked::CreateUObject(this, &UWarfrontMainMenuWidget::HandleBack))
        ];
}

TSharedRef<SWidget> UWarfrontMainMenuWidget::MakeMenuButton(
    const FText& Label,
    const FOnClicked& OnClicked) const
{
    return SNew(SButton)
        .ContentPadding(FMargin(18.0f, 15.0f))
        .ButtonColorAndOpacity(FSlateColor(FLinearColor(0.105f, 0.145f, 0.155f, 1.0f)))
        .OnClicked(OnClicked)
        [
            SNew(SHorizontalBox)
            + SHorizontalBox::Slot()
            .FillWidth(1.0f)
            .HAlign(HAlign_Left)
            .VAlign(VAlign_Center)
            [
                SNew(STextBlock)
                .Text(Label)
                .Font(FCoreStyle::GetDefaultFontStyle(FName(TEXT("Bold")), 18))
                .ColorAndOpacity(FSlateColor(FLinearColor(0.92f, 0.92f, 0.86f)))
                .Justification(ETextJustify::Left)
            ]
            + SHorizontalBox::Slot()
            .AutoWidth()
            .HAlign(HAlign_Right)
            .VAlign(VAlign_Center)
            [
                SNew(STextBlock)
                .Text(FText::FromString(TEXT("›")))
                .Font(FCoreStyle::GetDefaultFontStyle(FName(TEXT("Bold")), 26))
                .ColorAndOpacity(FSlateColor(FLinearColor(0.66f, 0.74f, 0.61f)))
            ]
        ];
}

void UWarfrontMainMenuWidget::ShowLoadingScreen()
{
    Content->ClearChildren();
    Content->AddSlot()
        .AutoHeight()
        .HAlign(HAlign_Center)
        .Padding(0.0f, 0.0f, 0.0f, 12.0f)
        [
            SNew(STextBlock)
            .Text(FText::FromString(TEXT("NACITANI BOJISTE...")))
            .Font(FCoreStyle::GetDefaultFontStyle(FName(TEXT("Bold")), 28))
            .ColorAndOpacity(FSlateColor(FLinearColor(0.88f, 0.83f, 0.69f)))
            .Justification(ETextJustify::Center)
        ];

    Content->AddSlot()
        .AutoHeight()
        .HAlign(HAlign_Center)
        [
            SNew(STextBlock)
            .Text(FText::FromString(TEXT("Teren • Atmosfera • Jednotky • Vozidla")))
            .Font(FCoreStyle::GetDefaultFontStyle(FName(TEXT("Regular")), 14))
            .ColorAndOpacity(FSlateColor(FLinearColor(0.64f, 0.72f, 0.70f)))
            .Justification(ETextJustify::Center)
        ];
}

void UWarfrontMainMenuWidget::SetUpdateAvailableVersion(const FString& Version)
{
    UpdateAvailableVersion = Version;
    if (Content.IsValid())
    {
        BuildMainMenu();
    }
}

FReply UWarfrontMainMenuWidget::HandleSinglePlayer()
{
    if (UWorld* World = GetWorld())
    {
        if (UWarfrontGameInstance* GameInstance =
                Cast<UWarfrontGameInstance>(World->GetGameInstance()))
        {
            GameInstance->BeginSinglePlayer();
        }
    }

    return FReply::Handled();
}

FReply UWarfrontMainMenuWidget::HandleMultiplayer()
{
    BuildMultiplayerScreen();
    return FReply::Handled();
}

FReply UWarfrontMainMenuWidget::HandleDevLog()
{
    BuildDevLogScreen();
    return FReply::Handled();
}

FReply UWarfrontMainMenuWidget::HandleUpdates()
{
    if (UWorld* World = GetWorld())
    {
        if (UWarfrontGameInstance* GameInstance =
                Cast<UWarfrontGameInstance>(World->GetGameInstance()))
        {
            GameInstance->OpenReleasesPage();
        }
    }

    return FReply::Handled();
}

FReply UWarfrontMainMenuWidget::HandleExit()
{
    if (UWorld* World = GetWorld())
    {
        if (UWarfrontGameInstance* GameInstance =
                Cast<UWarfrontGameInstance>(World->GetGameInstance()))
        {
            GameInstance->QuitGame();
        }
    }

    return FReply::Handled();
}

FReply UWarfrontMainMenuWidget::HandleBack()
{
    BuildMainMenu();
    return FReply::Handled();
}
