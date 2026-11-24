#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "WarfrontPlayerCharacter.generated.h"

UCLASS()
class WARFRONT_API AWarfrontPlayerCharacter : public ACharacter
{
    GENERATED_BODY()

public:
    AWarfrontPlayerCharacter();

protected:
    virtual void SetupPlayerInputComponent(UInputComponent* PlayerInputComponent) override;
    virtual float TakeDamage(
        float Damage,
        struct FDamageEvent const& DamageEvent,
        class AController* EventInstigator,
        class AActor* DamageCauser) override;

private:
    void MoveForward(float Value);
    void MoveRight(float Value);
    void TogglePause();
    void ToggleInventory();
    void Fire();
    void StartReload();
    void FinishReload();
    void UpdateCombatHud();

    float Health = 100.0f;
    int32 MagazineAmmo = 30;
    int32 ReserveAmmo = 120;
    float LastFireTime = -1.0f;
    FTimerHandle ReloadTimer;
};
