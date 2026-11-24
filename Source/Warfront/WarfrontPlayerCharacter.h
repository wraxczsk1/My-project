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

private:
    void MoveForward(float Value);
    void MoveRight(float Value);
    void TogglePause();
    void ToggleInventory();
};
