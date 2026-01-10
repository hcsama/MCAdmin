<script lang="ts">
    import { untrack } from 'svelte';
    import { fade } from 'svelte/transition';

    interface World {
        weather: string;
        weather_cycle: boolean;
    }

    let { world, serverOnline } = $props<{ 
        world: World, 
        serverOnline: boolean
    }>();

    let loading = $state(false);
    let lastWeatherCycle = $state(untrack(() => world.weather_cycle));
    let lastWeather = $state(untrack(() => world.weather));

    $effect(() => {
        if (world.weather_cycle !== lastWeatherCycle || world.weather !== lastWeather) {
            loading = false;
            lastWeatherCycle = world.weather_cycle;
            lastWeather = world.weather;
        }
    });

    let selectedDuration = $state('default');
    let statusMessage = $state('');
    let statusStyle = $state('');
    let statusTimeout: ReturnType<typeof setTimeout>;

    const statusStyles: Record<string, string> = {
        clear: 'bg-amber-50 dark:bg-amber-900/20 text-amber-600 dark:text-amber-400 border-amber-100 dark:border-amber-800/30',
        rain: 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400 border-blue-100 dark:border-blue-800/30',
        thunder: 'bg-purple-50 dark:bg-purple-900/20 text-purple-600 dark:text-purple-400 border-purple-100 dark:border-purple-800/30',
        enabled: 'bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400 border-green-100 dark:border-green-800/30',
        disabled: 'bg-red-50 dark:bg-red-900/20 text-red-600 dark:text-red-400 border-red-100 dark:border-red-800/30'
    };

    function showStatus(message: string, type: string) {
        if (statusTimeout) clearTimeout(statusTimeout);
        statusMessage = message;
        statusStyle = statusStyles[type] || statusStyles.enabled;
        statusTimeout = setTimeout(() => {
            statusMessage = '';
        }, 3000);
    }

    const durations = [
        { label: 'Default', value: 'default', ticks: null },
        { label: '1 Minute', value: '1m', ticks: 17 }, // ~16.6t
        { label: '1 Hour', value: '1h', ticks: 1000 },
        { label: '1 Day', value: '1d', ticks: 24000 }
    ];

    async function setWeather(type: string) {
        if (!serverOnline) return;
        loading = true;
        try {
            const durationObj = durations.find(d => d.value === selectedDuration);
            const res = await fetch('/api/world/weather', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    type, 
                    duration: durationObj?.ticks || null 
                })
            });
            if (!res.ok) throw new Error('Failed to set weather');
            showStatus(`Weather set to ${type}`, type);
        } catch (error) {
            console.error(error);
            loading = false;
        }
    }

    async function toggleWeatherCycle() {
        if (!serverOnline) return;
        const targetEnabled = !world.weather_cycle;
        loading = true;
        try {
            const res = await fetch('/api/world/weather-cycle', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ enabled: targetEnabled })
            });
            if (!res.ok) throw new Error('Failed to toggle weather cycle');
            showStatus(`Weather cycle ${targetEnabled ? 'enabled' : 'disabled'}`, targetEnabled ? 'enabled' : 'disabled');
        } catch (error) {
            console.error(error);
            loading = false;
        }
    }

    const weatherTypes = [
        { id: 'clear', label: 'Clear', icon: 'M12 3v1m0 16v1m9-9h-1M4 12H3m15.364-6.364l-.707.707M6.343 17.657l-.707.707m12.728 0l-.707-.707M6.343 6.343l-.707-.707M12 8a4 4 0 100 8 4 4 0 000-8z', color: 'bg-amber-100/50 text-amber-600 dark:bg-amber-900/20 dark:text-amber-400' },
        { id: 'rain', label: 'Rain', icon: 'M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z', color: 'bg-blue-100/50 text-blue-600 dark:bg-blue-900/20 dark:text-blue-400' }, // Using info icon as placeholder for rain if needed, but I'll use a better path
        { id: 'thunder', label: 'Thunder', icon: 'M13 10V3L4 14h7v7l9-11h-7z', color: 'bg-purple-100/50 text-purple-600 dark:bg-purple-900/20 dark:text-purple-400' }
    ];

    // Better rain icon path
    weatherTypes[1].icon = "M20 16.242c0 2.122-4 2.122-4 0 0-1.84 4-5.242 4-5.242s4 3.402 4 5.242c0 2.122-4 2.122-4 0zM12 16.242c0 2.122-4 2.122-4 0 0-1.84 4-5.242 4-5.242s4 3.402 4 5.242c0 2.122-4 2.122-4 0zM4 16.242c0 2.122-4 2.122-4 0 0-1.84 4-5.242 4-5.242s4 3.402 4 5.242c0 2.122-4 2.122-4 0z";
</script>

<div class="rounded-2xl border border-slate-200 bg-amber-50/20 p-6 shadow-sm backdrop-blur-sm transition-all dark:border-slate-800 dark:bg-amber-900/10 group/tile flex flex-col h-full">
    <div class="flex items-center justify-between mb-6">
        <div>
            <h2 class="text-lg font-semibold text-slate-900 dark:text-white">Weather</h2>
            <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Control world environment</p>
        </div>
        
        <div class="flex items-center gap-3">
            <span class="text-xs font-medium text-slate-500 dark:text-slate-400">
                {world.weather_cycle ? 'Cycle Active' : 'Frozen'}
            </span>
            <button 
                onclick={toggleWeatherCycle}
                disabled={!serverOnline || loading}
                class="relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed
                {world.weather_cycle ? 'bg-green-500' : 'bg-slate-200 dark:bg-slate-700'}"
                aria-label="Toggle Weather Cycle"
            >
                <span 
                    class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out
                    {world.weather_cycle ? 'translate-x-5' : 'translate-x-0'}"
                ></span>
            </button>
        </div>
    </div>

    <!-- Duration Selector -->
    <div class="mb-6">
        <span class="block text-[10px] font-bold uppercase tracking-widest text-slate-400 dark:text-slate-500 mb-2">
            Duration
        </span>
        <div class="grid grid-cols-4 gap-2">
            {#each durations as d}
                <button 
                    onclick={() => selectedDuration = d.value}
                    class="px-2 py-2 text-[10px] font-semibold rounded-xl transition-all border
                    {selectedDuration === d.value 
                        ? 'bg-green-600 border-green-600 text-white shadow-sm' 
                        : 'bg-white dark:bg-slate-800 border-slate-200 dark:border-slate-700 text-slate-600 dark:text-slate-400 hover:border-green-500'}"
                >
                    {d.label}
                </button>
            {/each}
        </div>
    </div>

    <!-- Weather Actions -->
    <div class="grid grid-cols-3 gap-3">
        {#each weatherTypes as type}
            <button 
                onclick={() => setWeather(type.id)}
                disabled={!serverOnline || loading}
                class="flex flex-col items-center justify-center p-4 rounded-2xl border border-transparent transition-all active:scale-95 disabled:opacity-50
                {type.color} group relative overflow-hidden"
            >
                <svg class="h-6 w-6 mb-2 transition-transform group-hover:scale-110" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d={type.icon} />
                </svg>
                <span class="text-xs font-bold uppercase tracking-wider">{type.label}</span>
            </button>
        {/each}
    </div>

    <div class="mt-auto min-h-[44px] flex items-end justify-center">
        {#if statusMessage}
            <div 
                transition:fade={{ duration: 200 }}
                class="w-full flex items-center justify-center gap-2 py-1.5 px-3 rounded-lg text-[11px] font-bold uppercase tracking-widest border {statusStyle} text-center"
            >
                <svg class="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                </svg>
                {statusMessage}
            </div>
        {/if}
    </div>
</div>
