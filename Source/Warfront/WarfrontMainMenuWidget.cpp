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
            .BorderBackgroundColor(FLinearColor(0.0f, 0.0f, 0.0f, 0.72f))
        ]
        + SOverlay::Slot()
        .HAlign(HAlign_Center)
        .VAlign(VAlign_Center)
        [
            SNew(SBorder)
            .BorderImage(FCoreStyle::Get().GetBrush("WhiteBrush"))
            .BorderBackgroundColor(FLinearColor(0.035f, 0.045f, 0.05f, 0.96f))
            .Padding(FMargin(42.0f))
            [
                SNew(SBox)
                .WidthOverride(560.0f)
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
            .Padding(0.0f, 0.0f, 0.0f, 22.0f)
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
        .Padding(0.0f, 0.0f, 0.0f, 28.0f)
        [
            SNew(STextBlock)
            .Text(FText::FromString(TEXT("VYBER REZIMU")))
            .Font(FCoreStyle::GetDefaultFontStyle(FName(TEXT("Regular")), 16))
            .ColorAndOpacity(FSlateColor(FLinearColor(0.62f, 0.68f, 0.66f)))
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
        .ContentPadding(FMargin(16.0f, 13.0f))
        .ButtonColorAndOpacity(FSlateColor(FLinearColor(0.18f, 0.23f, 0.22f, 1.0f)))
        .OnClicked(OnClicked)
        [
            SNew(STextBlock)
            .Text(Label)
            .Font(FCoreStyle::GetDefaultFontStyle(FName(TEXT("Bold")), 18))
            .ColorAndOpacity(FSlateColor(FLinearColor(0.91f, 0.91f, 0.86f)))
            .Justification(ETextJustify::Center)
        ];
}

void UWarfrontMainMenuWidget::ShowLoadingScreen()
{
    Content->ClearChildren();
    Content->AddSlot()
        .AutoHeight()
        .HAlign(HAlign_Center)
        [
            SNew(STextBlock)
            .Text(FText::FromString(TEXT("NACITANI BOJISTE...")))
            .Font(FCoreStyle::GetDefaultFontStyle(FName(TEXT("Bold")), 28))
            .ColorAndOpacity(FSlateColor(FLinearColor(0.88f, 0.83f, 0.69f)))
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
