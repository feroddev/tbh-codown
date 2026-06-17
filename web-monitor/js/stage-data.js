const DIFFICULTY_CODE = { Normal: 1, Nightmare: 2, Hell: 3, Torment: 4 };
const DIFFICULTY_ORDER = { Normal: 0, Nightmare: 1, Hell: 2, Torment: 3 };
const FARM_WAVE_SECONDS_ESTIMATE = 25;

export const RECOMMENDED_FARM_PRESET = {
  7: 1108,
  15: 1203,
  20: 1208,
  30: 1308,
  40: 2109,
  50: 2305,
  65: 3205,
  80: 4103,
};

/** @type {Array<import("./stage-data.js").StageEntry>} */
let stageCache = [];
/** @type {Map<number, import("./stage-data.js").StageEntry>} */
const stageByKey = new Map();

/**
 * @typedef {object} StageEntry
 * @property {string} name
 * @property {number} act
 * @property {number} stage
 * @property {string} difficulty
 * @property {number} enemyLevel
 * @property {boolean} isActBoss
 * @property {number} bossChestLevel
 * @property {number | null} bossChestDropPercent
 * @property {number} waves
 * @property {number} monsterHp
 * @property {number} requiredPlayerLevel
 * @property {number} cubeLevelRangeMin
 * @property {number} cubeLevelRangeMax
 * @property {number} difficultyScore
 * @property {number} estimatedTimeSec
 * @property {number} stageKey
 */

function compareFarmEntries(a, b) {
  const dropA = a.bossChestDropPercent ?? 0;
  const dropB = b.bossChestDropPercent ?? 0;
  if (dropB !== dropA) return dropB - dropA;
  if (a.waves !== b.waves) return a.waves - b.waves;
  if (a.monsterHp !== b.monsterHp) return a.monsterHp - b.monsterHp;
  if (a.difficultyScore !== b.difficultyScore) {
    return a.difficultyScore - b.difficultyScore;
  }
  if (a.estimatedTimeSec !== b.estimatedTimeSec) {
    return a.estimatedTimeSec - b.estimatedTimeSec;
  }
  return a.enemyLevel - b.enemyLevel || a.act - b.act || a.stage - b.stage;
}

export async function loadStages() {
  const candidates = ["./data/stages.json", "../src/data/stages.json"];
  stageCache = [];
  stageByKey.clear();

  for (const path of candidates) {
    try {
      const response = await fetch(path);
      if (!response.ok) continue;
      const data = await response.json();
      if (!Array.isArray(data)) continue;

      for (const item of data) {
        const difficultyCode = DIFFICULTY_CODE[item.difficulty];
        if (!difficultyCode) continue;
        const stageKey =
          difficultyCode * 1000 +
          Number(item.act) * 100 +
          Number(item.stage);
        const chestLevel = Number(item.boss_chest_level);
        const waves = Number(item.waves ?? item.stage ?? 1);
        const monsterHp = Number(item.monster_hp ?? item.enemy_level);
        const entry = {
          name: String(item.name),
          act: Number(item.act),
          stage: Number(item.stage),
          difficulty: String(item.difficulty),
          enemyLevel: Number(item.enemy_level),
          isActBoss: Boolean(item.is_act_boss),
          bossChestLevel: chestLevel,
          bossChestDropPercent:
            item.boss_chest_drop_percent != null
              ? Number(item.boss_chest_drop_percent)
              : null,
          waves,
          monsterHp,
          requiredPlayerLevel: Number(
            item.required_player_level ?? item.enemy_level,
          ),
          cubeLevelRangeMin: Number(
            item.cube_level_range_min ?? chestLevel - 10,
          ),
          cubeLevelRangeMax: Number(
            item.cube_level_range_max ?? chestLevel + 10,
          ),
          difficultyScore: DIFFICULTY_ORDER[item.difficulty] ?? 99,
          estimatedTimeSec: Number(
            item.estimated_time_sec ?? waves * FARM_WAVE_SECONDS_ESTIMATE,
          ),
          stageKey,
        };
        stageCache.push(entry);
        stageByKey.set(stageKey, entry);
      }
      return stageCache;
    } catch {
      /* try next path */
    }
  }

  throw new Error("Failed to load stages.json");
}

export function getStageByKey(stageKey) {
  return stageByKey.get(Number(stageKey)) ?? null;
}

export function stagesForLevel(level) {
  return stageCache
    .filter((item) => item.bossChestLevel === level && !item.isActBoss)
    .sort(compareFarmEntries);
}

export function recommendedStageForLevel(level) {
  const presetKey = RECOMMENDED_FARM_PRESET[level];
  if (presetKey != null) {
    const preset = stageByKey.get(presetKey);
    if (preset && !preset.isActBoss && preset.bossChestLevel === level) {
      return preset;
    }
  }
  const stages = stagesForLevel(level);
  return stages.length ? stages[0] : null;
}

export function bestStageKeyForLevel(level) {
  const stage = recommendedStageForLevel(level);
  return stage ? stage.stageKey : null;
}

export function isBestStageForChest(entry) {
  return bestStageKeyForLevel(entry.bossChestLevel) === entry.stageKey;
}

export function formatBossDropPercent(percent) {
  if (percent == null || !Number.isFinite(percent)) return "";
  return `${percent}%`;
}

export function formatStageLabel(entry, { includeStar = true, localizeDifficulty } = {}) {
  const dropPart = formatBossDropPercent(entry.bossChestDropPercent);
  const stagePart = `${entry.act}-${entry.stage}`;
  const diffPart = localizeDifficulty
    ? localizeDifficulty(entry.difficulty)
    : entry.difficulty;
  const core = dropPart
    ? `${dropPart} - ${stagePart} · ${diffPart}`
    : `${stagePart} · ${diffPart}`;
  if (includeStar && isBestStageForChest(entry)) {
    return `★ ${core}`;
  }
  return core;
}
