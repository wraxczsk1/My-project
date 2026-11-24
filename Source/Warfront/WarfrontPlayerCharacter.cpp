#include "WarfrontPlayerCharacter.h"

#include "Camera/CameraComponent.h"
#include "Components/CapsuleComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "GameFramework/Controller.h"
#include "DrawDebugHelpers.h"
#include "Engine/World.h"
#include "InputCoreTypes.h"
#include "Kismet/GameplayStatics.h"
#include "WarfrontGameInstance.h"

AWarfrontPlayerCharacter::AWarfrontPlayerCharacter()
{
    GetCapsuleComponent()->InitCapsuleSize(42.0f, 96.0f);
    bUseControllerRotationYaw = true;

    UCameraComponent* Camera = CreateDefaultSubobject<UCameraComponent>(TEXT("FirstPersonCamera"));
    Camera->SetupAttachment(GetCapsuleComponent());
    Camera->SetRelativeLocation(FVector(10.0f, 0.0f, 62.0f));
    Camera->bUsePawnControlRotation = true;

    UCharacterMovementComponent* Movement = GetCharacterMovement();
    Movement->bOrientRotationToMovement = false;
    Movement->MaxWalkSpeed = 560.0f;
    Movement->JumpZVelocity = 430.0f;
    Movement->AirControl = 0.25f;
}

void AWarfrontPlayerCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
    Super::SetupPlayerInputComponent(PlayerInputComponent);
    if (!PlayerInputComponent)
    {
        return;
    }

    PlayerInputComponent->BindAxis(TEXT("MoveForward"), this, &AWarfrontPlayerCharacter::MoveForward);
    PlayerInputComponent->BindAxis(TEXT("MoveRight"), this, &AWarfrontPlayerCharacter::MoveRight);
    PlayerInputComponent->BindAxis(TEXT("Turn"), this, &APawn::AddControllerYawInput);
    PlayerInputComponent->BindAxis(TEXT("LookUp"), this, &APawn::AddControllerPitchInput);
    PlayerInputComponent->BindAction(TEXT("Jump"), IE_Pressed, this, &ACharacter::Jump);
    PlayerInputComponent->BindAction(TEXT("Jump"), IE_Released, this, &ACharacter::StopJumping);
    PlayerInputComponent->BindAction(TEXT("Pause"), IE_Pressed, this, &AWarfrontPlayerCharacter::TogglePause);
    PlayerInputComponent->BindAction(TEXT("Inventory"), IE_Pressed, this, &AWarfrontPlayerCharacter::ToggleInventory);
    PlayerInputComponent->BindAction(TEXT("Fire"), IE_Pressed, this, &AWarfrontPlayerCharacter::Fire);
    PlayerInputComponent->BindAction(TEXT("Reload"), IE_Pressed, this, &AWarfrontPlayerCharacter::StartReload);
}

void AWarfrontPlayerCharacter::TogglePause()
{
    if (UWorld* World = GetWorld())
    {
        if (UWarfrontGameInstance* GameInstance =
                Cast<UWarfrontGameInstance>(World->GetGameInstance()))
        {
            GameInstance->TogglePauseMenu();
        }
    }
}

void AWarfrontPlayerCharacter::ToggleInventory()
{
    if (UWorld* World = GetWorld())
    {
        if (UWarfrontGameInstance* GameInstance =
                Cast<UWarfrontGameInstance>(World->GetGameInstance()))
        {
            GameInstance->ToggleInventory();
        }
    }
}

void AWarfrontPlayerCharacter::MoveForward(float Value)
{
    if (Controller && FMath::Abs(Value) > KINDA_SMALL_NUMBER)
    {
        const FRotator YawRotation(0.0f, Controller->GetControlRotation().Yaw, 0.0f);
        AddMovementInput(FRotationMatrix(YawRotation).GetUnitAxis(EAxis::X), Value);
    }
}

void AWarfrontPlayerCharacter::MoveRight(float Value)
{
    if (Controller && FMath::Abs(Value) > KINDA_SMALL_NUMBER)
    {
        const FRotator YawRotation(0.0f, Controller->GetControlRotation().Yaw, 0.0f);
        AddMovementInput(FRotationMatrix(YawRotation).GetUnitAxis(EAxis::Y), Value);
    }
}

void AWarfrontPlayerCharacter::Fire()
{
    UWorld* World = GetWorld();
    if (!World || Health <= 0.0f)
    {
        return;
    }

    const float GameTime = World->GetTimeSeconds();
    if (MagazineAmmo <= 0)
    {
        StartReload();
        return;
    }
    if (GameTime - LastFireTime < 0.09f)
    {
        return;
    }
    LastFireTime = GameTime;
    --MagazineAmmo;

    const FVector Start = GetActorLocation() + FVector(0.0f, 0.0f, 62.0f);
    const FVector Direction =
        Controller ? Controller->GetControlRotation().Vector() : GetActorForwardVector();
    const FVector End = Start + Direction * 50000.0f;

    FHitResult Hit;
    FCollisionQueryParams QueryParams(SCENE_QUERY_STAT(FireTrace), false, this);
    if (World->LineTraceSingleByChannel(Hit, Start, End, ECC_Visibility, QueryParams))
    {
        DrawDebugLine(World, Start, Hit.Location, FColor::Orange, false, 0.06f, 0, 1.5f);
        if (AActor* HitActor = Hit.GetActor())
        {
            UGameplayStatics::ApplyPointDamage(
                HitActor,
                34.0f,
                Direction,
                Hit,
                Controller,
                this,
                UDamageType::StaticClass());
        }
    }
    else
    {
        DrawDebugLine(World, Start, End, FColor::Orange, false, 0.06f, 0, 1.0f);
    }

    UpdateCombatHud();
}

void AWarfrontPlayerCharacter::StartReload()
{
    UWorld* World = GetWorld();
    if (!World || Health <= 0.0f || MagazineAmmo >= 30 || ReserveAmmo <= 0)
    {
        return;
    }
    if (World->GetTimerManager().IsTimerActive(ReloadTimer))
    {
        return;
    }

    World->GetTimerManager().SetTimer(
        ReloadTimer,
        this,
        &AWarfrontPlayerCharacter::FinishReload,
        1.8f,
        false);
}

void AWarfrontPlayerCharacter::FinishReload()
{
    const int32 Needed = 30 - MagazineAmmo;
    const int32 Loaded = FMath::Min(Needed, ReserveAmmo);
    MagazineAmmo += Loaded;
    ReserveAmmo -= Loaded;
    UpdateCombatHud();
}

float AWarfrontPlayerCharacter::TakeDamage(
    float Damage,
    FDamageEvent const& DamageEvent,
    AController* EventInstigator,
    AActor* DamageCauser)
{
    const float Applied = Super::TakeDamage(
        Damage,
        DamageEvent,
        EventInstigator,
        DamageCauser);
    Health = FMath::Clamp(Health - Applied, 0.0f, 100.0f);

    if (Health <= 0.0f)
    {
        DisableInput(Cast<APlayerController>(Controller));
    }
    UpdateCombatHud();
    return Applied;
}

void AWarfrontPlayerCharacter::UpdateCombatHud()
{
    if (UWorld* World = GetWorld())
    {
        if (UWarfrontGameInstance* GameInstance =
                Cast<UWarfrontGameInstance>(World->GetGameInstance()))
        {
            GameInstance->UpdateCombatStatus(
                FMath::RoundToInt(Health),
                MagazineAmmo,
                ReserveAmmo);
        }
    }
}
