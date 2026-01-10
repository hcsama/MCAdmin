<script lang="ts">
    import { untrack } from 'svelte';
    import { fade } from 'svelte/transition';

    interface Gamerules {
        rules: Record<string, boolean | number>;
        statuses: Record<string, string>;
    }

    let { gamerules, serverOnline } = $props<{ 
        gamerules: Gamerules, 
        serverOnline: boolean 
    }>();

    let loadingRules = $state<Record<string, boolean>>({});

    $effect(() => {
        // When the gamerules object updates (from SSE), clear local loading states
        // Ensure state dependency by touching gamerules
        gamerules;
        untrack(() => {
            loadingRules = {};
        });
    });

    const ruleDefinitions: Record<string, { label: string, description: string }> = {
        disableRaids: { label: "Disable Raids", description: "Prevents village raids from occurring." },
        announceAdvancements: { label: "Announce Advancements", description: "Shows achievements in server chat." },
        doFireTick: { label: "Fire Spread", description: "Fire spreads and naturally extinguishes." },
        doImmediateRespawn: { label: "Immediate Respawn", description: "Players respawn instantly without the death screen." },
        doLimitedCrafting: { label: "Limited Crafting", description: "Players can only craft recipes they have unlocked." },
        drowningDamage: { label: "Drowning Damage", description: "Players take damage when they run out of air." },
        enderPearlsVanishOnDeath: { label: "Pearls Vanish on Death", description: "Ender pearls vanish when the tossing player dies." },
        fallDamage: { label: "Fall Damage", description: "Players take damage from falling." },
        fireDamage: { label: "Fire Damage", description: "Players take damage from fire and lava." },
        forgiveDeadPlayers: { label: "Forgive Dead Players", description: "Aggressive mobs reset when target dies." },
        freezeDamage: { label: "Freeze Damage", description: "Players take damage from powder snow freezing." },
        globalSoundEvents: { label: "Global Sounds", description: "Sounds like Wither spawn are heard by all layers." },
        keepInventory: { label: "Keep Inventory", description: "Keep items and XP after dying." },
        lavaSourceConversion: { label: "Lava Conversion", description: "Allows new lava source blocks to form." },
        naturalRegeneration: { label: "Natural Regen", description: "Regenerate health naturally from food." },
        projectilesCanBreakBlocks: { label: "Projectiles Break Blocks", description: "Projectiles can break certain blocks." },
        showDeathMessages: { label: "Death Messages", description: "Displays death messages in chat." },
        snowAccumulationHeight: { label: "Snow Height", description: "Max layers of snow (0-3)." },
        universalAnger: { label: "Universal Anger", description: "Angry mobs attack any nearby player." },
        waterSourceConversion: { label: "Water Conversion", description: "Allows infinite water sources." }
    };

    const categories = [
        {
            name: "World Physics",
            icon: "M13 10V3L4 14h7v7l9-11h-7z",
            rules: ["doFireTick", "lavaSourceConversion", "waterSourceConversion", "projectilesCanBreakBlocks", "snowAccumulationHeight"]
        },
        {
            name: "Survival & Health",
            icon: "M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z",
            rules: ["fallDamage", "fireDamage", "drowningDamage", "freezeDamage", "naturalRegeneration", "keepInventory"]
        },
        {
            name: "Mob Behavior",
            icon: "M12 9v3m0 0v3m0-3h3m-3 0H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z",
            rules: ["disableRaids", "enderPearlsVanishOnDeath", "forgiveDeadPlayers", "universalAnger"]
        },
        {
            name: "System & UI",
            icon: "M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z",
            rules: ["announceAdvancements", "doImmediateRespawn", "doLimitedCrafting", "globalSoundEvents", "showDeathMessages"]
        }
    ];

    async function toggleRule(ruleId: string, currentValue: boolean | number) {
        if (!serverOnline || loadingRules[ruleId]) return;
        
        const newValue = typeof currentValue === 'boolean' ? !currentValue : currentValue;
        loadingRules[ruleId] = true;

        try {
            const res = await fetch(`/api/world/gamerules/${ruleId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ value: newValue })
            });
            if (!res.ok) throw new Error(`Failed to update ${ruleId}`);
        } catch (error) {
            console.error(error);
            loadingRules[ruleId] = false;
        }
    }

    async function setNumericRule(ruleId: string, value: number) {
        if (!serverOnline || loadingRules[ruleId]) return;
        loadingRules[ruleId] = true;
        try {
            const res = await fetch(`/api/world/gamerules/${ruleId}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ value: value })
            });
            if (!res.ok) throw new Error(`Failed to update ${ruleId}`);
        } catch (error) {
            console.error(error);
            loadingRules[ruleId] = false;
        }
    }
</script>

<div class="col-span-full rounded-2xl border border-slate-200 bg-white/40 p-6 shadow-sm backdrop-blur-sm transition-all dark:border-slate-800 dark:bg-slate-900/40">
    <div class="flex items-center justify-between mb-8">
        <div>
            <h2 class="text-xl font-bold text-slate-900 dark:text-white">Gamerules Management</h2>
            <p class="text-sm text-slate-500 dark:text-slate-400 mt-1">Configure world behavior and gameplay mechanics</p>
        </div>
        <div class="flex items-center gap-2 px-3 py-1.5 rounded-full bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
            <span class="relative flex h-2 w-2">
                <span class="animate-ping absulute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                <span class="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
            </span>
            <span class="text-[10px] font-bold uppercase tracking-widest text-slate-500 dark:text-slate-400">Live Sync</span>
        </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-8">
        {#each categories as cat}
            <div class="flex flex-col gap-4">
                <div class="flex items-center gap-2 pb-2 border-b border-slate-200 dark:border-slate-800">
                    <svg class="h-4 w-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={cat.icon} />
                    </svg>
                    <h3 class="text-xs font-bold uppercase tracking-[0.2em] text-slate-400 dark:text-slate-500">{cat.name}</h3>
                </div>

                <div class="flex flex-col gap-3">
                    {#each cat.rules as ruleId}
                        {@const def = ruleDefinitions[ruleId]}
                        {@const value = gamerules.rules[ruleId]}
                        {@const status = gamerules.statuses[ruleId] || 'pending'}
                        
                        <div class="flex flex-col gap-1.5 p-3 rounded-xl border transition-all 
                            {status === 'pending' ? 'bg-slate-100/30 dark:bg-slate-800/10 border-slate-100 dark:border-slate-900 opacity-60' : 'bg-slate-50/50 dark:bg-slate-800/30 border-slate-100 dark:border-slate-800/50 hover:border-slate-200 dark:hover:border-slate-700'}">
                            <div class="flex items-center justify-between">
                                <span class="text-xs font-semibold {status === 'pending' ? 'text-slate-400 dark:text-slate-500' : 'text-slate-700 dark:text-slate-300'}">
                                    {def.label}
                                </span>
                                
                                {#if status === 'unsupported'}
                                    <span class="text-[10px] font-bold text-slate-400 dark:text-slate-600 bg-slate-100 dark:bg-slate-800/50 px-2 py-0.5 rounded-md border border-slate-200/50 dark:border-slate-800/50">
                                        N/A
                                    </span>
                                {:else if status === 'pending'}
                                    <div class="flex h-5 items-center">
                                        <div class="h-1.5 w-8 rounded-full bg-slate-200 dark:bg-slate-700 animate-pulse"></div>
                                    </div>
                                {:else if typeof value === 'boolean'}
                                    <button 
                                        onclick={() => toggleRule(ruleId, value)}
                                        disabled={!serverOnline || loadingRules[ruleId]}
                                        class="relative inline-flex h-5 w-9 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-1 disabled:opacity-50
                                        {value ? 'bg-green-600' : 'bg-rose-600'}"
                                        aria-label={`Toggle ${def.label}`}
                                        aria-pressed={value}
                                    >
                                        <span 
                                            class="pointer-events-none inline-block h-4 w-4 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out
                                            {value ? 'translate-x-4' : 'translate-x-0'}"
                                        ></span>
                                    </button>
                                {:else if typeof value === 'number'}
                                    <div class="flex items-center gap-1">
                                        {#each [0, 1, 2, 3] as stop}
                                            <button 
                                                onclick={() => setNumericRule(ruleId, stop)}
                                                disabled={!serverOnline || loadingRules[ruleId]}
                                                class="w-5 h-5 flex items-center justify-center rounded text-[8px] font-bold transition-all
                                                {value === stop 
                                                    ? 'bg-green-600 text-white' 
                                                    : 'bg-slate-200 dark:bg-slate-700 text-slate-500 dark:text-slate-400 hover:bg-slate-300 dark:hover:bg-slate-600'}"
                                                aria-label={`Set ${def.label} to ${stop}`}
                                                aria-pressed={value === stop}
                                            >
                                                {stop}
                                            </button>
                                        {/each}
                                    </div>
                                {/if}
                            </div>
                            <p class="text-[10px] text-slate-500 dark:text-slate-400 leading-tight">
                                {def.description}
                            </p>
                        </div>
                    {/each}
                </div>
            </div>
        {/each}
    </div>
</div>
