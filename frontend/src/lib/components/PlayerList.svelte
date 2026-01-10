<script lang="ts">
import { untrack } from 'svelte';

    interface Player {
        name: string;
        whitelisted: boolean;
        avatar_url?: string;
    }

    interface PlayerState extends Player {
        status: 'joined' | 'left' | 'normal';
    }

    let { players = [] } = $props<{ players: Player[] }>();

    let displayPlayers = $state<PlayerState[]>([]);
    let lastPlayerNames = $state(new Set<string>());

    $effect(() => {
        // We only want to react to 'players' prop changes
        const currentNames = players.map(p => p.name);
        const currentNamesSet = new Set(currentNames);
        
        untrack(() => {
            // Find new players
            const joined = currentNames.filter(name => !lastPlayerNames.has(name));
            // Find left players
            const left = Array.from(lastPlayerNames).filter(name => !currentNamesSet.has(name));

            if (joined.length > 0 || left.length > 0) {
                // Build the new display list
                let newDisplay: PlayerState[] = players.map(p => {
                    const isJoined = joined.includes(p.name);
                    // If it was already in displayPlayers as 'joined', keep it as 'joined' until timeout
                    const existing = displayPlayers.find(dp => dp.name === p.name);
                    return {
                        ...p,
                        whitelisted: p.whitelisted,
                        avatar_url: p.avatar_url,
                        status: (isJoined || (existing?.status === 'joined')) ? 'joined' : 'normal'
                    } as PlayerState;
                });

                // Add left players temporarily if they aren't already marked as 'left'
                left.forEach(name => {
                    const existing = displayPlayers.find(dp => dp.name === name);
                    if (!existing || existing.status !== 'left') {
                        newDisplay.push({ 
                            name, 
                            whitelisted: existing?.whitelisted || false, 
                            avatar_url: existing?.avatar_url,
                            status: 'left' 
                        });
                    }
                });

                displayPlayers = newDisplay;
                lastPlayerNames = currentNamesSet;

                // Clear 'joined' and 'left' statuses after a while
                const timer = setTimeout(() => {
                    displayPlayers = displayPlayers
                        .filter(p => p.status !== 'left')
                        .map(p => ({ ...p, status: 'normal' }));
                }, 3000);

                return () => clearTimeout(timer);
            } else if (displayPlayers.length === 0 && players.length > 0) {
                // Initial load
                displayPlayers = players.map(p => ({ ...p, status: 'normal' }));
                lastPlayerNames = currentNamesSet;
            } else {
                // Just update whitelisted status and avatar if changed
                displayPlayers = displayPlayers.map(dp => {
                    const latest = players.find(p => p.name === dp.name);
                    if (latest) {
                        return { 
                            ...dp, 
                            whitelisted: latest.whitelisted,
                            avatar_url: latest.avatar_url
                        };
                    }
                    return dp;
                });
            }
        });
    });

</script>

<div class="mt-4 flex flex-col gap-2">
    {#each displayPlayers as player (player.name)}
        <div 
            class="flex items-center justify-between rounded-xl border border-slate-100 bg-white p-3 shadow-sm transition-all duration-700 dark:border-slate-800 dark:bg-slate-800/50 
            {player.status === 'joined' ? 'ring-2 ring-green-400 bg-green-50 dark:bg-green-900/20 scale-105' : ''} 
            {player.status === 'left' ? 'ring-2 ring-red-400 bg-red-50 dark:bg-red-900/20 animate-pulse' : ''}"
        >
            <div class="flex items-center gap-3">
                <div class="h-8 w-8 rounded-lg overflow-hidden bg-slate-100 flex items-center justify-center dark:bg-slate-700 transition-colors shrink-0
                    {player.status === 'joined' ? 'bg-green-100 dark:bg-green-800' : ''}
                    {player.status === 'left' ? 'bg-red-100 dark:bg-red-800' : ''}"
                >
                    {#if player.avatar_url}
                        <img 
                            src={player.avatar_url} 
                            alt={player.name}
                            class="h-full w-full object-contain p-0.5"
                            onerror={(e) => (e.currentTarget.style.display = 'none')}
                        />
                    {/if}
                    <svg class="h-4 w-4 text-slate-500 
                        {player.status === 'joined' ? 'text-green-600' : ''} 
                        {player.status === 'left' ? 'text-red-600' : ''}
                        {player.avatar_url ? 'hidden' : ''}" 
                        fill="none" viewBox="0 0 24 24" stroke="currentColor"
                    >
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                </div>
                <div class="flex flex-col">
                    <span class="text-sm font-semibold text-slate-700 dark:text-slate-200">{player.name}</span>
                    {#if player.whitelisted}
                        <div class="flex items-center gap-1 text-[9px] font-bold uppercase tracking-wider text-blue-500 dark:text-blue-400/80">
                            <svg class="h-2.5 w-2.5" fill="currentColor" viewBox="0 0 20 20">
                                <path fill-rule="evenodd" d="M2.166 4.999A11.954 11.954 0 0010 1.944 11.954 11.954 0 0017.834 5c.11.65.166 1.32.166 2.001 0 5.225-3.34 9.67-8 11.317C5.34 16.67 2 12.225 2 7c0-.682.057-1.35.166-2.001zm11.541 3.708a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clip-rule="evenodd" />
                            </svg>
                            Whitelisted
                        </div>
                    {/if}
                </div>
            </div>
            
            {#if player.status === 'joined'}
                <div class="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-green-100 dark:bg-green-800/40">
                    <span class="relative flex h-2 w-2">
                        <span class="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                        <span class="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                    </span>
                    <span class="text-[10px] font-bold uppercase tracking-wider text-green-700 dark:text-green-400">Joined</span>
                </div>
            {:else if player.status === 'left'}
                 <div class="flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-red-100 dark:bg-red-800/40">
                    <span class="text-[10px] font-bold uppercase tracking-wider text-red-700 dark:text-red-400">Left</span>
                </div>
            {/if}
        </div>
    {/each}
    {#if players.length === 0 && displayPlayers.length === 0}
        <div class="flex flex-col items-center justify-center py-8 text-slate-400 opacity-40">
            <svg class="h-10 w-10 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z" />
            </svg>
            <span class="text-sm font-medium uppercase tracking-wider">No one is online</span>
        </div>
    {/if}
</div>
