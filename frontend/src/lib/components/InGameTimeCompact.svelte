<script lang="ts">
    import { untrack } from 'svelte';
    import Clock from './Clock.svelte';
    
    interface Server {
        online: boolean;
    }
    
    interface World {
        time: number;
        time_formatted: string;
        phase: string;
        days: number;
        daylight_cycle: boolean;
    }
    
    let { server, world } = $props<{ server: Server, world: World }>();

    let loading = $state(false);
    let lastDaylightCycle = $state(untrack(() => world.daylight_cycle));

    $effect(() => {
        if (world.daylight_cycle !== lastDaylightCycle) {
            loading = false;
            lastDaylightCycle = world.daylight_cycle;
        }
    });

    async function toggleDaylightCycle() {
        if (!server.online) return;
        loading = true;
        try {
            const res = await fetch('/api/world/daylight-cycle', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ enabled: !world.daylight_cycle })
            });
            if (!res.ok) throw new Error('Failed to toggle daylight cycle');
        } catch (error) {
            console.error(error);
            loading = false;
        }
    }
    
    const phaseConfig: Record<string, { color: string, bg: string, label: string }> = {
        Dawn: { color: 'text-orange-200', bg: 'bg-amber-50 dark:bg-amber-900/20', label: 'Dawn' },
        Day: { color: 'text-yellow-500', bg: 'bg-sky-50 dark:bg-sky-900/20', label: 'Day' },
        Dusk: { color: 'text-rose-300', bg: 'bg-indigo-50 dark:bg-indigo-900/20', label: 'Dusk' },
        Night: { color: 'text-indigo-500', bg: 'bg-purple-50 dark:bg-purple-900/20', label: 'Night' }
    };
    
    let config = $derived(phaseConfig[world.phase] || phaseConfig.Day);
</script>

<div class="flex items-center gap-3">
    {#if server.online}
        <!-- Analogue Clock -->
        <div class="h-10 w-10 shrink-0">
            <Clock ticks={world.time} />
        </div>
        
        <!-- Digital Time & Phase Display -->
        <div class="flex flex-col justify-center">
            <div class="flex items-center gap-2">
                <span class="text-xl font-bold tracking-tight text-slate-900 dark:text-white leading-none">
                    {world.time_formatted}
                </span>
                
                <!-- Phase Icon -->
                <div class={`${config.color}`}>
                    {#if world.phase === 'Day'}
                        <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364-6.364l-.707.707M6.343 17.657l-.707.707m12.728 0l-.707-.707M6.343 6.343l-.707-.707M12 8a4 4 0 100 8 4 4 0 000-8z" />
                        </svg>
                    {:else if world.phase === 'Night'}
                        <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                        </svg>
                    {:else}
                        <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364-6.364l-.707.707M6.343 17.657l-.707.707m12.728 0l-.707-.707M6.343 6.343l-.707-.707M12 8a4 4 0 100 8 4 4 0 000-8z" opacity="0.5" />
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 18h16" />
                        </svg>
                    {/if}
                </div>
            </div>
            <div class="flex items-center gap-2 mt-1">
                <span class={`text-[10px] font-bold uppercase tracking-widest ${config.color} leading-none opacity-80`}>
                    {config.label} (Day {world.days})
                </span>

                <button 
                    onclick={toggleDaylightCycle}
                    disabled={!server.online || loading}
                    class="group relative flex h-3 w-6 shrink-0 items-center rounded-full p-0.5 transition-colors duration-200 focus:outline-none focus:ring-1 focus:ring-offset-1 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer
                    {world.daylight_cycle ? 'bg-green-500 dark:bg-green-600 focus:ring-green-500' : 'bg-red-500 dark:bg-red-600 focus:ring-red-500'}"
                    title={world.daylight_cycle ? "Stop Time Progression" : "Resume Time Progression"}
                >
                    <span class="sr-only">Toggle Daylight Cycle</span>
                    <span 
                        class="pointer-events-none inline-block h-2 w-2 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out
                        {world.daylight_cycle ? 'translate-x-3' : 'translate-x-0'}"
                    ></span>
                </button>
            </div>
        </div>
    {:else}
        <div class="flex items-center gap-2 text-slate-400 opacity-50">
            <svg class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <span class="text-sm font-medium">Offline</span>
        </div>
    {/if}
</div>
