#include "WarfrontGameMode.h"

#include "WarfrontPlayerCharacter.h"

AWarfrontGameMode::AWarfrontGameMode()
{
    DefaultPawnClass = AWarfrontPlayerCharacter::StaticClass();
}
