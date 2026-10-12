#include "global.h"
#include "constants/abilities.h"
#include "constants/battle_move_effects.h"
#include "constants/hold_effects.h"
#include "constants/items.h"
#include "constants/moves.h"
#include "constants/species.h"
#include "battle.h"
#include "berry.h"
#include "data2.h"
#include "event_data.h"
#include "item.h"
#include "pokemon.h"
#include "ewram.h"

extern u16 gBattleTypeFlags;
extern struct BattlePokemon gBattleMons[4];
extern u16 gCurrentMove;
extern u8 gCritMultiplier;
extern u16 gBattleWeather;
extern struct BattleEnigmaBerry gEnigmaBerries[];
extern u16 gBattleMovePower;
extern u16 gTrainerBattleOpponent;

// Masks for getting PP Up count, also PP Max values
const u8 gPPUpReadMasks[] = {0x03, 0x0c, 0x30, 0xc0};

// Masks for setting PP Up count
const u8 gPPUpWriteMasks[] = {0xFC, 0xF3, 0xCF, 0x3F};

// Values added to PP Up count
const u8 gPPUpValues[] = {0x01, 0x04, 0x10, 0x40};

const u8 gStatStageRatios[][2] =
{
    {10, 40}, // -6
    {10, 35}, // -5
    {10, 30}, // -4
    {10, 25}, // -3
    {10, 20}, // -2
    {10, 15}, // -1
    {10, 10}, //  0
    {15, 10}, //  1
    {20, 10}, //  2
    {25, 10}, //  3
    {30, 10}, //  4
    {35, 10}, //  5
    {40, 10}  //  6
};

const u8 unknownGameFreakAbbrev_820825E[] = _("ゲーフリ");

const u8 gHoldEffectToType[][2] =
{
    {HOLD_EFFECT_BUG_POWER,      TYPE_BUG},
    {HOLD_EFFECT_STEEL_POWER,    TYPE_STEEL},
    {HOLD_EFFECT_GROUND_POWER,   TYPE_GROUND},
    {HOLD_EFFECT_ROCK_POWER,     TYPE_ROCK},
    {HOLD_EFFECT_GRASS_POWER,    TYPE_GRASS},
    {HOLD_EFFECT_DARK_POWER,     TYPE_DARK},
    {HOLD_EFFECT_FIGHTING_POWER, TYPE_FIGHTING},
    {HOLD_EFFECT_ELECTRIC_POWER, TYPE_ELECTRIC},
    {HOLD_EFFECT_WATER_POWER,    TYPE_WATER},
    {HOLD_EFFECT_FLYING_POWER,   TYPE_FLYING},
    {HOLD_EFFECT_POISON_POWER,   TYPE_POISON},
    {HOLD_EFFECT_ICE_POWER,      TYPE_ICE},
    {HOLD_EFFECT_GHOST_POWER,    TYPE_GHOST},
    {HOLD_EFFECT_PSYCHIC_POWER,  TYPE_PSYCHIC},
    {HOLD_EFFECT_FIRE_POWER,     TYPE_FIRE},
    {HOLD_EFFECT_DRAGON_POWER,   TYPE_DRAGON},
    {HOLD_EFFECT_NORMAL_POWER,   TYPE_NORMAL}
};

u8 GetBattlerSide(u8 bank);

#define APPLY_STAT_MOD(var, mon, stat, statIndex)                                   \
{                                                                                   \
    (var) = (stat) * (gStatStageRatios)[(mon)->statStages[(statIndex)]][0];         \
    (var) /= (gStatStageRatios)[(mon)->statStages[(statIndex)]][1];                 \
}

#define BADGE_BOOST(badge, stat, bank) ({ \
if (!(gBattleTypeFlags & (BATTLE_TYPE_LINK | BATTLE_TYPE_BATTLE_TOWER | BATTLE_TYPE_EREADER_TRAINER))) \
{ \
    if ((gBattleTypeFlags & BATTLE_TYPE_TRAINER) \
    && gTrainerBattleOpponent != SECRET_BASE_OPPONENT \
    && FlagGet(FLAG_BADGE0##badge##_GET) \
    && GetBattlerSide(bank) == B_SIDE_PLAYER) \
        (stat) = (110 * (stat)) / 100; \
} \
})

static bool8 IsMovePhysical(u32 move, u8 type)
{
    switch (move)
    {
    // Physical moves whose types were special before Generation IV.
    case MOVE_FIRE_PUNCH:
    case MOVE_FLAME_WHEEL:
    case MOVE_BLAZE_KICK:
    case MOVE_SACRED_FIRE:
    case MOVE_WATERFALL:
    case MOVE_CRABHAMMER:
    case MOVE_DIVE:
    case MOVE_CLAMP:
    case MOVE_RAZOR_LEAF:
    case MOVE_VINE_WHIP:
    case MOVE_BULLET_SEED:
    case MOVE_NEEDLE_ARM:
    case MOVE_LEAF_BLADE:
    case MOVE_THUNDER_PUNCH:
    case MOVE_SPARK:
    case MOVE_VOLT_TACKLE:
    case MOVE_ICE_PUNCH:
    case MOVE_ICE_BALL:
    case MOVE_OUTRAGE:
    case MOVE_DRAGON_CLAW:
    case MOVE_BITE:
    case MOVE_CRUNCH:
    case MOVE_PURSUIT:
    case MOVE_THIEF:
    case MOVE_FAINT_ATTACK:
    case MOVE_KNOCK_OFF:
    case MOVE_BEAT_UP:
    case MOVE_LICK:
    case MOVE_SHADOW_PUNCH:
    case MOVE_ASTONISH:
    case MOVE_STEEL_WING:
    case MOVE_METAL_CLAW:
    case MOVE_METEOR_MASH:
    case MOVE_IRON_TAIL:
    case MOVE_POISON_FANG:
    case MOVE_POISON_TAIL:
        return TRUE;

    // Special moves whose types were physical before Generation IV.
    case MOVE_RAZOR_WIND:
    case MOVE_HYPER_BEAM:
    case MOVE_SONIC_BOOM:
    case MOVE_ACID:
    case MOVE_SLUDGE:
    case MOVE_SWIFT:
    case MOVE_NIGHT_SHADE:
    case MOVE_SMOG:
    case MOVE_TRI_ATTACK:
    case MOVE_SNORE:
    case MOVE_GUST:
    case MOVE_SHADOW_BALL:
    case MOVE_AEROBLAST:
    case MOVE_SLUDGE_BOMB:
    case MOVE_MUD_SLAP:
    case MOVE_AIR_CUTTER:
    case MOVE_SILVER_WIND:
    case MOVE_SIGNAL_BEAM:
    case MOVE_MUD_SHOT:
    case MOVE_ANCIENT_POWER:
    case MOVE_DOOM_DESIRE:
    case MOVE_HIDDEN_POWER:
    case MOVE_WEATHER_BALL:
    case MOVE_HYPER_VOICE:
    case MOVE_UPROAR:
        return FALSE;
    default:
        return type < TYPE_MYSTERY;
    }
}

static bool8 IsMoveSpecial(u32 move, u8 type)
{
    return type != TYPE_MYSTERY && !IsMovePhysical(move, type);
}

s32 CalculateBaseDamage(struct BattlePokemon *attacker, struct BattlePokemon *defender, u32 move, u16 sideStatus, u16 powerOverride, u8 typeOverride, u8 bankAtk, u8 bankDef)
{
    u32 i;
    s32 damage = 0;
    s32 damageHelper;
    u8 type;
    u16 attack, defense;
    u16 spAttack, spDefense;
    u8 defenderHoldEffect;
    u8 defenderHoldEffectParam;
    u8 attackerHoldEffect;
    u8 attackerHoldEffectParam;

    if (!powerOverride)
        gBattleMovePower = gBattleMoves[move].power;
    else
        gBattleMovePower = powerOverride;

    if (!typeOverride)
        type = gBattleMoves[move].type;
    else
        type = typeOverride & 0x3F;

    attack = attacker->attack;
    defense = defender->defense;
    spAttack = attacker->spAttack;
    spDefense = defender->spDefense;

    if (attacker->item == ITEM_ENIGMA_BERRY)
    {
        attackerHoldEffect = gEnigmaBerries[bankAtk].holdEffect;
        attackerHoldEffectParam = gEnigmaBerries[bankAtk].holdEffectParam;
    }
    else
    {
        attackerHoldEffect = ItemId_GetHoldEffect(attacker->item);
        attackerHoldEffectParam = ItemId_GetHoldEffectParam(attacker->item);
    }

    if (defender->item == ITEM_ENIGMA_BERRY)
    {
        defenderHoldEffect = gEnigmaBerries[bankDef].holdEffect;
        defenderHoldEffectParam = gEnigmaBerries[bankDef].holdEffectParam;
    }
    else
    {
        defenderHoldEffect = ItemId_GetHoldEffect(defender->item);
        defenderHoldEffectParam = ItemId_GetHoldEffectParam(defender->item);
    }

    if (attacker->ability == ABILITY_HUGE_POWER || attacker->ability == ABILITY_PURE_POWER)
        attack *= 2;

    BADGE_BOOST(1, attack, bankAtk);
    BADGE_BOOST(5, defense, bankDef);
    BADGE_BOOST(7, spAttack, bankAtk);
    BADGE_BOOST(7, spDefense, bankDef);

    for (i = 0; i < 17; i++)
    {
        if (attackerHoldEffect == gHoldEffectToType[i][0]
            && type == gHoldEffectToType[i][1])
        {
            if (IsMovePhysical(move, type))
                attack = (attack * (attackerHoldEffectParam + 100)) / 100;
            else if (IsMoveSpecial(move, type))
                spAttack = (spAttack * (attackerHoldEffectParam + 100)) / 100;
            break;
        }
    }

    if (attackerHoldEffect == HOLD_EFFECT_CHOICE_BAND && IsMovePhysical(move, type))
        attack = (150 * attack) / 100;
    if (attackerHoldEffect == HOLD_EFFECT_SOUL_DEW && !(gBattleTypeFlags & BATTLE_TYPE_BATTLE_TOWER) && (attacker->species == SPECIES_LATIAS || attacker->species == SPECIES_LATIOS))
        spAttack = (150 * spAttack) / 100;
    if (defenderHoldEffect == HOLD_EFFECT_SOUL_DEW && !(gBattleTypeFlags & BATTLE_TYPE_BATTLE_TOWER) && (defender->species == SPECIES_LATIAS || defender->species == SPECIES_LATIOS))
        spDefense = (150 * spDefense) / 100;
    if (attackerHoldEffect == HOLD_EFFECT_DEEP_SEA_TOOTH && attacker->species == SPECIES_CLAMPERL)
        spAttack *= 2;
    if (defenderHoldEffect == HOLD_EFFECT_DEEP_SEA_SCALE && defender->species == SPECIES_CLAMPERL)
        spDefense *= 2;
    if (attackerHoldEffect == HOLD_EFFECT_LIGHT_BALL && attacker->species == SPECIES_PIKACHU)
        spAttack *= 2;
    if (defenderHoldEffect == HOLD_EFFECT_METAL_POWDER && defender->species == SPECIES_DITTO)
        defense *= 2;
    if (attackerHoldEffect == HOLD_EFFECT_THICK_CLUB && (attacker->species == SPECIES_CUBONE || attacker->species == SPECIES_MAROWAK))
        attack *= 2;
    if (defender->ability == ABILITY_THICK_FAT && (type == TYPE_FIRE || type == TYPE_ICE))
        gBattleMovePower /= 2;
    if (attacker->ability == ABILITY_HUSTLE)
        attack = (150 * attack) / 100;
    if (attacker->ability == ABILITY_PLUS && AbilityBattleEffects(ABILITYEFFECT_FIELD_SPORT, 0, ABILITY_MINUS, 0, 0))
        spAttack = (150 * spAttack) / 100;
    if (attacker->ability == ABILITY_MINUS && AbilityBattleEffects(ABILITYEFFECT_FIELD_SPORT, 0, ABILITY_PLUS, 0, 0))
        spAttack = (150 * spAttack) / 100;
    if (attacker->ability == ABILITY_GUTS && attacker->status1)
        attack = (150 * attack) / 100;
    if (defender->ability == ABILITY_MARVEL_SCALE && defender->status1)
        defense = (150 * defense) / 100;
    if (type == TYPE_ELECTRIC && AbilityBattleEffects(ABILITYEFFECT_FIELD_SPORT, 0, 0, 0xFD, 0))
        gBattleMovePower /= 2;
    if (type == TYPE_FIRE && AbilityBattleEffects(ABILITYEFFECT_FIELD_SPORT, 0, 0, 0xFE, 0))
        gBattleMovePower /= 2;
    if (type == TYPE_GRASS && attacker->ability == ABILITY_OVERGROW && attacker->hp <= (attacker->maxHP / 3))
        gBattleMovePower = (150 * gBattleMovePower) / 100;
    if (type == TYPE_FIRE && attacker->ability == ABILITY_BLAZE && attacker->hp <= (attacker->maxHP / 3))
        gBattleMovePower = (150 * gBattleMovePower) / 100;
    if (type == TYPE_WATER && attacker->ability == ABILITY_TORRENT && attacker->hp <= (attacker->maxHP / 3))
        gBattleMovePower = (150 * gBattleMovePower) / 100;
    if (type == TYPE_BUG && attacker->ability == ABILITY_SWARM && attacker->hp <= (attacker->maxHP / 3))
        gBattleMovePower = (150 * gBattleMovePower) / 100;
    if (gBattleMoves[gCurrentMove].effect == EFFECT_EXPLOSION)
        defense /= 2;

    if (IsMovePhysical(move, type)) // Move-based physical category
    {
        if (gCritMultiplier == 2)
        {
            if (attacker->statStages[STAT_STAGE_ATK] > 6)
                APPLY_STAT_MOD(damage, attacker, attack, STAT_STAGE_ATK)
            else
                damage = attack;
        }
        else
            APPLY_STAT_MOD(damage, attacker, attack, STAT_STAGE_ATK)

        damage = damage * gBattleMovePower;
        damage *= (2 * attacker->level / 5 + 2);

        if (gCritMultiplier == 2)
        {
            if (defender->statStages[STAT_STAGE_DEF] < 6)
                APPLY_STAT_MOD(damageHelper, defender, defense, STAT_STAGE_DEF)
            else
                damageHelper = defense;
        }
        else
            APPLY_STAT_MOD(damageHelper, defender, defense, STAT_STAGE_DEF)

        damage = damage / damageHelper;
        damage /= 50;

        if ((attacker->status1 & STATUS1_BURN) && attacker->ability != ABILITY_GUTS)
            damage /= 2;

        if ((sideStatus & SIDE_STATUS_REFLECT) && gCritMultiplier == 1)
        {
            if ((gBattleTypeFlags & BATTLE_TYPE_DOUBLE) && CountAliveMons(2) == 2)
                damage = 2 * (damage / 3);
            else
                damage /= 2;
        }

        if ((gBattleTypeFlags & BATTLE_TYPE_DOUBLE) && gBattleMoves[move].target == 8 && CountAliveMons(2) == 2)
            damage /= 2;

        // moves always do at least 1 damage.
        if (damage == 0)
            damage = 1;
    }

    if (type == TYPE_MYSTERY)
        damage = 0; // is ??? type. does 0 damage.

    if (IsMoveSpecial(move, type)) // Move-based special category
    {
        if (gCritMultiplier == 2)
        {
            if (attacker->statStages[STAT_STAGE_SPATK] > 6)
                APPLY_STAT_MOD(damage, attacker, spAttack, STAT_STAGE_SPATK)
            else
                damage = spAttack;
        }
        else
            APPLY_STAT_MOD(damage, attacker, spAttack, STAT_STAGE_SPATK)

        damage = damage * gBattleMovePower;
        damage *= (2 * attacker->level / 5 + 2);

        if (gCritMultiplier == 2)
        {
            if (defender->statStages[STAT_STAGE_SPDEF] < 6)
                APPLY_STAT_MOD(damageHelper, defender, spDefense, STAT_STAGE_SPDEF)
            else
                damageHelper = spDefense;
        }
        else
            APPLY_STAT_MOD(damageHelper, defender, spDefense, STAT_STAGE_SPDEF)

        damage = (damage / damageHelper);
        damage /= 50;

        if ((sideStatus & SIDE_STATUS_LIGHTSCREEN) && gCritMultiplier == 1)
        {
            if ((gBattleTypeFlags & BATTLE_TYPE_DOUBLE) && CountAliveMons(2) == 2)
                damage = 2 * (damage / 3);
            else
                damage /= 2;
        }

        if ((gBattleTypeFlags & BATTLE_TYPE_DOUBLE) && gBattleMoves[move].target == 8 && CountAliveMons(2) == 2)
            damage /= 2;


    }

    // Weather and Flash Fire affect damaging moves of their type, regardless of category.
    if (gBattleMovePower != 0)
    {
        if (!AbilityBattleEffects(ABILITYEFFECT_FIELD_SPORT, 0, ABILITY_CLOUD_NINE, 0, 0)
            && !AbilityBattleEffects(ABILITYEFFECT_FIELD_SPORT, 0, ABILITY_AIR_LOCK, 0, 0))
        {
            if (gBattleWeather & B_WEATHER_RAIN_TEMPORARY)
            {
                if (type == TYPE_FIRE)
                    damage /= 2;
                else if (type == TYPE_WATER)
                    damage = (15 * damage) / 10;
            }

            if (move == MOVE_SOLAR_BEAM
                && (gBattleWeather & (B_WEATHER_RAIN | B_WEATHER_SANDSTORM | B_WEATHER_HAIL_TEMPORARY)))
                damage /= 2;

            if (gBattleWeather & B_WEATHER_SUN)
            {
                if (type == TYPE_FIRE)
                    damage = (15 * damage) / 10;
                else if (type == TYPE_WATER)
                    damage /= 2;
            }
        }

        if ((eBattleFlagsArr.arr[bankAtk] & 1) && type == TYPE_FIRE)
            damage = (15 * damage) / 10;
    }

    return damage + 2;
}
