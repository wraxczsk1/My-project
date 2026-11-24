#include "WarfrontMainMenuWidget.h"

#include "Engine/Texture2D.h"
#include "Engine/World.h"
#include "HAL/IConsoleManager.h"
#include "Styling/CoreStyle.h"
#include "WarfrontGameInstance.h"
#include "Widgets/Input/SButton.h"
#include "Widgets/Layout/SBox.h"
#include "Widgets/Layout/SBorder.h"
#include "Widgets/SOverlay.h"
#include "Widgets/SCanvas.h"
#include "Widgets/SBoxPanel.h"
#include "Widgets/Images/SImage.h"
#include "Widgets/SBoxPanel.h"
#include "Widgets/Notifications/SProgressBar.h"
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

    FullscreenBackground = SNew(SBorder)
        .BorderImage(FCoreStyle::Get().GetBrush("WhiteBrush"))
        .BorderBackgroundColor(FLinearColor(0.018f, 0.026f, 0.032f, 0.94f));

    MenuCardBorder = SNew(SBorder)
        .BorderImage(FCoreStyle::Get().GetBrush("WhiteBrush"))
        .BorderBackgroundColor(FLinearColor(0.052f, 0.074f, 0.082f, 0.98f))
        .Padding(FMargin(38.0f))
        [
            SNew(SBox)
            .WidthOverride(620.0f)
            [
                Content.ToSharedRef()
            ]
        ];

    CombatStatusText = SNew(STextBlock)
        .Text(FText::FromString(TEXT("HEALTH 100  |  CZ 805 BREN  30 / 120")))
        .Font(FCoreStyle::GetDefaultFontStyle(FName(TEXT("Bold")), 18))
        .ColorAndOpacity(FSlateColor(FLinearColor(0.88f, 0.90f, 0.86f, 0.95f)));

    CompassStatusText = SNew(STextBlock)
        .Text(FText::FromString(TEXT("NW 315  |  N 000  |  NE 045")))
        .Font(FCoreStyle::GetDefaultFontStyle(FName(TEXT("Bold")), 14))
        .ColorAndOpacity(FSlateColor(FLinearColor(0.84f, 0.86f, 0.82f, 0.95f)));

    ObjectiveStatusText = SNew(STextBlock)
        .Text(FText::FromString(TEXT("OBJECTIVE\nSECURE THE FORWARD LINE")))
        .Font(FCoreStyle::GetDefaultFontStyle(FName(TEXT("Bold")), 13))
        .ColorAndOpacity(FSlateColor(FLinearColor(0.88f, 0.83f, 0.69f, 0.95f)))
        .Justification(ETextJustify::Right);

    GameplayOverlay = SNew(SOverlay)
        .Visibility(EVisibility::Collapsed)
        + SOverlay::Slot()
        .HAlign(HAlign_Left)
        .VAlign(VAlign_Bottom)
        .Padding(28.0f, 0.0f, 0.0f, 30.0f)
        [
            SNew(SBorder)
            .BorderImage(FCoreStyle::Get().GetBrush("WhiteBrush"))
            .BorderBackgroundColor(FLinearColor(0.018f, 0.025f, 0.028f, 0.82f))
            .Padding(FMargin(16.0f, 10.0f))
            [
                SNew(SVerticalBox)
                + SVerticalBox::Slot().AutoHeight()
                [
                    CombatStatusText.ToSharedRef()
                ]
                + SVerticalBox::Slot().AutoHeight().Padding(0.0f, 8.0f, 0.0f, 0.0f)
                [
                    SNew(SProgressBar)
                    .Percent(1.0f)
                    .FillColorAndOpacity(FLinearColor(0.42f, 0.72f, 0.43f, 0.95f))
                ]
            ]
        ]
        + SOverlay::Slot()
        .HAlign(HAlign_Center)
        .VAlign(VAlign_Top)
        .Padding(0.0f, 18.0f, 0.0f, 0.0f)
        [
            SNew(SBorder)
            .BorderImage(FCoreStyle::Get().GetBrush("WhiteBrush"))
            .BorderBackgroundColor(FLinearColor(0.018f, 0.025f, 0.028f, 0.68f))
            .Padding(FMargin(14.0f, 7.0f))
            [
                CompassStatusText.ToSharedRef()
            ]
        ]
        + SOverlay::Slot()
        .HAlign(HAlign_Right)
        .VAlign(VAlign_Top)
        .Padding(0.0f, 18.0f, 28.0f, 0.0f)
        [
            SNew(SBorder)
            .BorderImage(FCoreStyle::Get().GetBrush("WhiteBrush"))
            .BorderBackgroundColor(FLinearColor(0.018f, 0.025f, 0.028f, 0.72f))
            .Padding(FMargin(14.0f, 10.0f))
            [
                ObjectiveStatusText.ToSharedRef()
            ]
        ]
        + SOverlay::Slot()
        .HAlign(HAlign_Center)
        .VAlign(VAlign_Center)
        [
            SNew(STextBlock)
            .Text(FText::FromString(TEXT("+")))
            .Font(FCoreStyle::GetDefaultFontStyle(FName(TEXT("Bold")), 24))
            .ColorAndOpacity(FSlateColor(FLinearColor(0.88f, 0.90f, 0.86f, 0.9f)))
        ];

    return SNew(SOverlay)
        + SOverlay::Slot()
        .HAlign(HAlign_Fill)
        .VAlign(VAlign_Fill)
        [
            FullscreenBackground.ToSharedRef()
        ]
        + SOverlay::Slot()
        .HAlign(HAlign_Center)
        .VAlign(VAlign_Center)
        [
            MenuCardBorder.ToSharedRef()
        ]
        + SOverlay::Slot()
        .HAlign(HAlign_Fill)
        .VAlign(VAlign_Fill)
        [
            GameplayOverlay.ToSharedRef()
        ];
}

void UWarfrontMainMenuWidget::BuildMainMenu()
{
    if (DevLogWindow.IsValid())
    {
        DevLogWindow->SetVisibility(EVisibility::Visible);
    }
    if (GameplayOverlay.IsValid())
    {
        GameplayOverlay->SetVisibility(EVisibility::Collapsed);
    }
    if (FullscreenBackground.IsValid())
    {
        FullscreenBackground->SetBorderBackgroundColor(FLinearColor(0.018f, 0.026f, 0.032f, 0.94f));
    }
    if (MenuCardBorder.IsValid())
    {
        MenuCardBorder->SetBorderBackgroundColor(FLinearColor(0.052f, 0.074f, 0.082f, 0.98f));
        MenuCardBorder->SetPadding(FMargin(38.0f));
    }

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
        .Text(FText::FromString(TEXT("TACTICAL SINGLE-PLAYER EXPERIENCE")))
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
                FText::FromString(TEXT("SETTINGS")),
                FOnClicked::CreateUObject(this, &UWarfrontMainMenuWidget::HandleSettings))
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
                    ? FText::FromString(TEXT("CHECK FOR UPDATES"))
                    : FText::FromString(FString(TEXT("UPDATE AVAILABLE ")) + UpdateAvailableVersion),
                FOnClicked::CreateUObject(this, &UWarfrontMainMenuWidget::HandleUpdates))
        ];

    Content->AddSlot()
        .AutoHeight()
        .Padding(0.0f, 5.0f)
        [
            MakeMenuButton(
                FText::FromString(TEXT("EXIT GAME")),
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
    if (DevLogWindow.IsValid())
    {
        DevLogWindow->SetVisibility(EVisibility::Collapsed);
    }
    if (GameplayOverlay.IsValid())
    {
        GameplayOverlay->SetVisibility(EVisibility::Visible);
    }
    if (FullscreenBackground.IsValid())
    {
        FullscreenBackground->SetBorderBackgroundColor(FLinearColor(0.0f, 0.0f, 0.0f, 0.0f));
    }
    if (MenuCardBorder.IsValid())
    {
        MenuCardBorder->SetBorderBackgroundColor(FLinearColor(0.0f, 0.0f, 0.0f, 0.0f));
        MenuCardBorder->SetPadding(FMargin(0.0f));
    }

    Content->ClearChildren();
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
                TEXT("HEALTH %d  |  CZ 805 BREN  %d / %d"),
                Health,
                MagazineAmmo,
                ReserveAmmo)));
    }
}

void UWarfrontMainMenuWidget::BuildPauseMenu()
{
    if (DevLogWindow.IsValid())
    {
        DevLogWindow->SetVisibility(EVisibility::Collapsed);
    }
    if (GameplayOverlay.IsValid())
    {
        GameplayOverlay->SetVisibility(EVisibility::Collapsed);
    }
    if (FullscreenBackground.IsValid())
    {
        FullscreenBackground->SetBorderBackgroundColor(FLinearColor(0.018f, 0.026f, 0.032f, 0.94f));
    }
    if (MenuCardBorder.IsValid())
    {
        MenuCardBorder->SetBorderBackgroundColor(FLinearColor(0.052f, 0.074f, 0.082f, 0.98f));
        MenuCardBorder->SetPadding(FMargin(38.0f));
    }

    Content->ClearChildren();
    Content->AddSlot()
        .AutoHeight()
        .HAlign(HAlign_Center)
        .Padding(0.0f, 0.0f, 0.0f, 18.0f)
        [
            SNew(STextBlock)
            .Text(FText::FromString(TEXT("PAUSED")))
            .Font(FCoreStyle::GetDefaultFontStyle(FName(TEXT("Bold")), 38))
            .ColorAndOpacity(FSlateColor(FLinearColor(0.88f, 0.83f, 0.69f)))
        ];

    Content->AddSlot().AutoHeight().Padding(0.0f, 5.0f)
        [
            MakeMenuButton(
                FText::FromString(TEXT("RESUME GAME")),
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
                FText::FromString(TEXT("INVENTORY")),
                FOnClicked::CreateLambda([this]()
                {
                    BuildInventoryScreen();
                    return FReply::Handled();
                }))
        ];

    Content->AddSlot().AutoHeight().Padding(0.0f, 5.0f)
        [
            MakeMenuButton(
                FText::FromString(TEXT("BACK TO MAIN MENU")),
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
    TSharedPtr<SCanvas> InventoryGrid;

    if (DevLogWindow.IsValid())
    {
        DevLogWindow->SetVisibility(EVisibility::Collapsed);
    }
    if (GameplayOverlay.IsValid())
    {
        GameplayOverlay->SetVisibility(EVisibility::Collapsed);
    }
    if (FullscreenBackground.IsValid())
    {
        FullscreenBackground->SetBorderBackgroundColor(FLinearColor(0.018f, 0.026f, 0.032f, 0.94f));
    }
    if (MenuCardBorder.IsValid())
    {
        MenuCardBorder->SetBorderBackgroundColor(FLinearColor(0.052f, 0.074f, 0.082f, 0.98f));
        MenuCardBorder->SetPadding(FMargin(38.0f));
    }

    Content->ClearChildren();
    Content->AddSlot()
        .AutoHeight()
        .HAlign(HAlign_Center)
        .Padding(0.0f, 0.0f, 0.0f, 16.0f)
        [
            SNew(STextBlock)
            .Text(FText::FromString(TEXT("LOADOUT  //  INVENTORY")))
            .Font(FCoreStyle::GetDefaultFontStyle(FName(TEXT("Bold")), 34))
            .ColorAndOpacity(FSlateColor(FLinearColor(0.88f, 0.83f, 0.69f)))
        ];
    Content->AddSlot()
        .AutoHeight()
        .HAlign(HAlign_Center)
        .Padding(0.0f, 0.0f, 0.0f, 10.0f)
        [
            SNew(STextBlock)
            .Text(FText::FromString(TEXT("EQUIPMENT  68/120 kg  |  PRIMARY  |  SECONDARY  |  QUICK ITEMS")))
            .Font(FCoreStyle::GetDefaultFontStyle(FName(TEXT("Regular")), 13))
            .ColorAndOpacity(FSlateColor(FLinearColor(0.64f, 0.72f, 0.70f)))
        ];
    Content->AddSlot()
        .AutoHeight()
        .Padding(0.0f, 4.0f)
        [
            SNew(SBox)
            .WidthOverride(600.0f)
            .HeightOverride(420.0f)
            [
                SNew(SBorder)
                .BorderImage(FCoreStyle::Get().GetBrush("WhiteBrush"))
                .BorderBackgroundColor(FLinearColor(0.035f, 0.047f, 0.050f, 0.98f))
                .Padding(FMargin(16.0f))
                [
                    SAssignNew(InventoryGrid, SCanvas)
                ]
            ]
        ];

    if (InventoryGrid.IsValid())
    {
        const float StartX = 24.0f;
        const float StartY = 20.0f;
        for (int32 Row = 0; Row < 7; ++Row)
        {
            for (int32 Column = 0; Column < 10; ++Column)
            {
                InventoryGrid->AddSlot()
                    .Position(FVector2D(StartX + Column * 52.0f, StartY + Row * 52.0f))
                    .Size(FVector2D(48.0f, 48.0f))
                    [
                        SNew(SBorder)
                        .BorderImage(FCoreStyle::Get().GetBrush("WhiteBrush"))
                        .BorderBackgroundColor(FLinearColor(0.09f, 0.13f, 0.14f, 0.65f))
                        .Padding(FMargin(1.0f))
                    ];
            }
        }

        InventoryGrid->AddSlot()
            .Position(FVector2D(StartX, StartY))
            .Size(FVector2D(208.0f, 104.0f))
            [
                SNew(SBorder)
                .BorderImage(FCoreStyle::Get().GetBrush("WhiteBrush"))
                .BorderBackgroundColor(FLinearColor(0.18f, 0.24f, 0.22f, 0.95f))
                .Padding(FMargin(8.0f))
                [
                    SNew(STextBlock)
                    .Text(FText::FromString(TEXT("CZ 805 BREN\n4 x 2")))
                    .Font(FCoreStyle::GetDefaultFontStyle(FName(TEXT("Bold")), 13))
                    .ColorAndOpacity(FSlateColor(FLinearColor(0.88f, 0.83f, 0.69f)))
                    .Justification(ETextJustify::Center)
                ]
            ];

        InventoryGrid->AddSlot()
            .Position(FVector2D(StartX + 260.0f, StartY))
            .Size(FVector2D(104.0f, 104.0f))
            [
                SNew(SBorder)
                .BorderImage(FCoreStyle::Get().GetBrush("WhiteBrush"))
                .BorderBackgroundColor(FLinearColor(0.15f, 0.20f, 0.19f, 0.95f))
                .Padding(FMargin(8.0f))
                [
                    SNew(STextBlock)
                    .Text(FText::FromString(TEXT("P-10 C\n2 x 2")))
                    .Font(FCoreStyle::GetDefaultFontStyle(FName(TEXT("Bold")), 12))
                    .ColorAndOpacity(FSlateColor(FLinearColor(0.88f, 0.83f, 0.69f)))
                    .Justification(ETextJustify::Center)
                ]
            ];

        const TArray<FText> SmallItems = {
            FText::FromString(TEXT("HELM")),
            FText::FromString(TEXT("BANDAZ")),
            FText::FromString(TEXT("GRANAT")),
            FText::FromString(TEXT("OPTIKA")),
            FText::FromString(TEXT("NABOJ"))
        };
        for (int32 Index = 0; Index < SmallItems.Num(); ++Index)
        {
            InventoryGrid->AddSlot()
                .Position(FVector2D(StartX + 416.0f + (Index % 2) * 52.0f,
                    StartY + (Index / 2) * 52.0f))
                .Size(FVector2D(48.0f, 48.0f))
                [
                    SNew(SBorder)
                    .BorderImage(FCoreStyle::Get().GetBrush("WhiteBrush"))
                    .BorderBackgroundColor(FLinearColor(0.12f, 0.16f, 0.15f, 0.95f))
                    .Padding(FMargin(4.0f))
                    [
                        SNew(STextBlock)
                        .Text(SmallItems[Index])
                        .Font(FCoreStyle::GetDefaultFontStyle(FName(TEXT("Bold")), 8))
                        .ColorAndOpacity(FSlateColor(FLinearColor(0.78f, 0.82f, 0.79f)))
                        .Justification(ETextJustify::Center)
                    ]
                ];
        }
    }

    Content->AddSlot().AutoHeight().Padding(0.0f, 12.0f)
        [
            MakeMenuButton(
                FText::FromString(TEXT("CLOSE INVENTORY")),
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

void UWarfrontMainMenuWidget::BuildSettingsScreen()
{
    if (GameplayOverlay.IsValid())
    {
        GameplayOverlay->SetVisibility(EVisibility::Collapsed);
    }
    if (DevLogWindow.IsValid())
    {
        DevLogWindow->SetVisibility(EVisibility::Collapsed);
    }
    if (FullscreenBackground.IsValid())
    {
        FullscreenBackground->SetBorderBackgroundColor(FLinearColor(0.018f, 0.026f, 0.032f, 0.94f));
    }
    if (MenuCardBorder.IsValid())
    {
        MenuCardBorder->SetBorderBackgroundColor(FLinearColor(0.052f, 0.074f, 0.082f, 0.98f));
        MenuCardBorder->SetPadding(FMargin(38.0f));
    }

    Content->ClearChildren();
    Content->AddSlot().AutoHeight().HAlign(HAlign_Center).Padding(0.0f, 0.0f, 0.0f, 18.0f)
        [
            SNew(STextBlock)
            .Text(FText::FromString(TEXT("SETTINGS")))
            .Font(FCoreStyle::GetDefaultFontStyle(FName(TEXT("Bold")), 38))
            .ColorAndOpacity(FSlateColor(FLinearColor(0.88f, 0.83f, 0.69f)))
        ];

    Content->AddSlot().AutoHeight().Padding(0.0f, 5.0f)
        [
            SNew(STextBlock)
            .Text(FText::FromString(
                TEXT("GRAPHICS\n")
                TEXT("VIEW DISTANCE  ·  SHADOWS  ·  POST PROCESS  ·  TEXTURES  ·  EFFECTS\n\n")
                TEXT("AUDIO\n")
                TEXT("MASTER 100%  ·  EFFECTS 100%  ·  MUSIC 80%\n\n")
                TEXT("CONTROLS\n")
                TEXT("WASD MOVE  ·  MOUSE LOOK  ·  LMB FIRE  ·  R RELOAD  ·  TAB INVENTORY  ·  ESC PAUSE")))
            .Font(FCoreStyle::GetDefaultFontStyle(FName(TEXT("Regular")), 16))
            .ColorAndOpacity(FSlateColor(FLinearColor(0.78f, 0.82f, 0.79f)))
            .AutoWrapText(true)
        ];

    auto ApplyGraphicsQuality = [this](int32 Quality)
    {
        const FString Value = FString::FromInt(Quality);
        IConsoleManager::Get().FindConsoleVariable(TEXT("sg.ViewDistanceQuality"))->Set(*Value);
        IConsoleManager::Get().FindConsoleVariable(TEXT("sg.ShadowQuality"))->Set(*Value);
        IConsoleManager::Get().FindConsoleVariable(TEXT("sg.PostProcessQuality"))->Set(*Value);
        IConsoleManager::Get().FindConsoleVariable(TEXT("sg.TextureQuality"))->Set(*Value);
        IConsoleManager::Get().FindConsoleVariable(TEXT("sg.EffectsQuality"))->Set(*Value);
        IConsoleManager::Get().FindConsoleVariable(TEXT("sg.FoliageQuality"))->Set(*Value);
    };

    Content->AddSlot().AutoHeight().Padding(0.0f, 5.0f)
        [
            MakeMenuButton(
                FText::FromString(TEXT("LOW GRAPHICS")),
                FOnClicked::CreateLambda([ApplyGraphicsQuality]()
                {
                    ApplyGraphicsQuality(0);
                    return FReply::Handled();
                }))
        ];
    Content->AddSlot().AutoHeight().Padding(0.0f, 5.0f)
        [
            MakeMenuButton(
                FText::FromString(TEXT("MEDIUM GRAPHICS")),
                FOnClicked::CreateLambda([ApplyGraphicsQuality]()
                {
                    ApplyGraphicsQuality(2);
                    return FReply::Handled();
                }))
        ];
    Content->AddSlot().AutoHeight().Padding(0.0f, 5.0f)
        [
            MakeMenuButton(
                FText::FromString(TEXT("HIGH GRAPHICS")),
                FOnClicked::CreateLambda([ApplyGraphicsQuality]()
                {
                    ApplyGraphicsQuality(3);
                    return FReply::Handled();
                }))
        ];

    Content->AddSlot().AutoHeight().Padding(0.0f, 5.0f)
        [
            MakeMenuButton(
                FText::FromString(TEXT("RESET CONTROLS")),
                FOnClicked::CreateLambda([]()
                {
                    if (IConsoleVariable* Sensitivity =
                        IConsoleManager::Get().FindConsoleVariable(TEXT("Input.MouseSensitivity")))
                    {
                        Sensitivity->Set(1.0f);
                    }
                    return FReply::Handled();
                }))
        ];

    Content->AddSlot().AutoHeight().Padding(0.0f, 12.0f)
        [
            MakeMenuButton(
                FText::FromString(TEXT("BACK TO MENU")),
                FOnClicked::CreateUObject(this, &UWarfrontMainMenuWidget::HandleBack))
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
            .Text(FText::FromString(TEXT("Online multiplayer is not available yet.")))
            .Font(FCoreStyle::GetDefaultFontStyle(FName(TEXT("Regular")), 16))
            .ColorAndOpacity(FSlateColor(FLinearColor(0.72f, 0.76f, 0.73f)))
            .Justification(ETextJustify::Center)
        ];

    Content->AddSlot()
        .AutoHeight()
        [
            MakeMenuButton(
                FText::FromString(TEXT("BACK TO MENU")),
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
            .Text(FText::FromString(TEXT("DEV LOG")))
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
                TEXT("0.1.3 - Procedural battlefield with forests and roads.\n")
                TEXT("Volumetric clouds, atmosphere, sunlight and fog.\n")
                TEXT("Main menu, loading screen and playable single-player.\n")
                TEXT("Multiplayer is not available yet.")))
            .Font(FCoreStyle::GetDefaultFontStyle(FName(TEXT("Regular")), 16))
            .ColorAndOpacity(FSlateColor(FLinearColor(0.72f, 0.76f, 0.73f)))
            .AutoWrapText(true)
        ];

    Content->AddSlot()
        .AutoHeight()
        [
            MakeMenuButton(
                FText::FromString(TEXT("BACK TO MENU")),
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
            .Text(FText::FromString(TEXT("LOADING BATTLEFIELD...")))
            .Font(FCoreStyle::GetDefaultFontStyle(FName(TEXT("Bold")), 28))
            .ColorAndOpacity(FSlateColor(FLinearColor(0.88f, 0.83f, 0.69f)))
            .Justification(ETextJustify::Center)
        ];

    Content->AddSlot()
        .AutoHeight()
        .HAlign(HAlign_Center)
        [
            SNew(STextBlock)
            .Text(FText::FromString(TEXT("Terrain • Atmosphere • Units • Vehicles")))
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

FReply UWarfrontMainMenuWidget::HandleSettings()
{
    BuildSettingsScreen();
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
