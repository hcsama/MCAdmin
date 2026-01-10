<script lang="ts">
    import { untrack } from 'svelte';
    let { ticks } = $props<{ ticks: number }>();
    
    // Minecraft 0 is 6:00 AM (180 degrees for hour hand)
    let hours = $derived(((ticks / 1000) + 6) % 24);
    let minutes = $derived(((ticks % 1000) / 1000) * 60);
    
    let targetHourDeg = $derived((hours % 12) * 30);
    let targetMinuteDeg = $derived(minutes * 6);

    let hourDeg = $state(untrack(() => targetHourDeg));
    let minuteDeg = $state(untrack(() => targetMinuteDeg));

    // Stabilize rotation by tracking the last target rather than current rotation modulo
    let lastTargetHour = untrack(() => targetHourDeg);
    let lastTargetMinute = untrack(() => targetMinuteDeg);

    $effect(() => {
        // Hour hand
        const currentTargetHour = targetHourDeg;
        let hourDelta = (currentTargetHour - lastTargetHour) % 360;
        if (hourDelta < 0) hourDelta += 360;
        
        if (hourDelta > 0.01) { // Threshold to prevent floating point jitter
            hourDeg += hourDelta;
            lastTargetHour = currentTargetHour;
        }

        // Minute hand
        const currentTargetMinute = targetMinuteDeg;
        let minuteDelta = (currentTargetMinute - lastTargetMinute) % 360;
        if (minuteDelta < 0) minuteDelta += 360;
        
        if (minuteDelta > 0.01) {
            minuteDeg += minuteDelta;
            lastTargetMinute = currentTargetMinute;
        }
    });
</script>

<div class="h-full w-full">
    <svg viewBox="0 0 100 100" class="h-full w-full drop-shadow-sm">
        <!-- Face -->
        <circle cx="50" cy="50" r="45" class="fill-white stroke-slate-200 stroke-2 dark:fill-slate-800 dark:stroke-slate-700" />
        
        <!-- Hour Markers -->
        {#each Array(12) as _, i}
            <line 
                x1="50" y1="10" x2="50" y2="15" 
                class="stroke-slate-300 dark:stroke-slate-600"
                transform="rotate({i * 30} 50 50)"
            />
        {/each}

        <!-- Minute Hand -->
        <line 
            x1="50" y1="50" x2="50" y2="15" 
            class="stroke-slate-400 stroke-[2px] transition-transform duration-500 ease-in-out dark:stroke-slate-500"
            style="transform-origin: 50px 50px; transform: rotate({minuteDeg}deg)"
        />

        <!-- Hour Hand -->
        <line 
            x1="50" y1="50" x2="50" y2="25" 
            class="stroke-slate-900 stroke-[3px] transition-transform duration-500 ease-in-out dark:stroke-slate-100"
            style="transform-origin: 50px 50px; transform: rotate({hourDeg}deg)"
        />

        <!-- Center Hub -->
        <circle cx="50" cy="50" r="3" class="fill-slate-900 dark:fill-slate-100" />
    </svg>
</div>
