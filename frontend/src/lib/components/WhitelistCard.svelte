<script lang="ts">
    import { untrack } from 'svelte';
    import { fly, fade } from 'svelte/transition';

    interface Player {
        name: string;
        avatar_url?: string;
    }

    interface WhitelistState {
        enabled: boolean;
        members: Player[];
    }

    let { whitelist, serverOnline, onlinePlayers = [] } = $props<{ 
        whitelist: WhitelistState, 
        serverOnline: boolean,
        onlinePlayers: Player[]
    }>();
    
    let newMember = $state('');
    let loading = $state(false);
    let lastWhitelistState = $state(untrack(() => JSON.stringify(whitelist)));

    let statusMessage = $state('');
    let statusStyle = $state('');
    let statusTimeout: ReturnType<typeof setTimeout>;

    function showStatus(message: string, success: boolean) {
        statusMessage = message;
        
        const lower = message.toLowerCase();
        if (lower.includes('added') || lower.includes('removed') || lower.includes('turned on')) {
            statusStyle = 'text-green-600 bg-green-50 dark:bg-green-900/20 dark:text-green-400';
        } else if (lower.includes('already') || lower.includes('was not') || lower.includes('is not')) {
            statusStyle = 'text-amber-600 bg-amber-50 dark:bg-amber-900/20 dark:text-amber-400';
        } else {
            statusStyle = 'text-red-600 bg-red-50 dark:bg-red-900/20 dark:text-red-400';
        }
        
        if (statusTimeout) clearTimeout(statusTimeout);
        statusTimeout = setTimeout(() => {
            statusMessage = '';
        }, 4000);
    }

    $effect(() => {
        const currentState = JSON.stringify(whitelist);
        if (currentState !== lastWhitelistState) {
            loading = false;
            lastWhitelistState = currentState;
        }
    });

    // Online players not already in the whitelist
    let suggestions = $derived(
        onlinePlayers.filter(p => !whitelist.members.some(m => m.name === p.name))
    );

    async function toggleWhitelist() {
        if (!serverOnline) return;
        loading = true;
        try {
            const res = await fetch('/api/whitelist/toggle', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ enabled: !whitelist.enabled })
            });
            const data = await res.json();
            if (res.ok) {
                showStatus(data.message || `Whitelist ${!whitelist.enabled ? 'enabled' : 'disabled'}`, data.success);
                if (!data.success) loading = false; // Reset if the command was rejected by RCON
            } else {
                throw new Error(data.detail || 'Failed to toggle whitelist');
            }
        } catch (error: any) {
            console.error(error);
            showStatus(error.message || 'Connection error', false);
            loading = false;
        }
    }

    async function addMember(name?: string) {
        const targetName = (name || newMember).trim();
        if (!targetName || !serverOnline) return;
        
        newMember = '';
        loading = true;
        try {
            const res = await fetch('/api/whitelist/members', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name: targetName })
            });
            const data = await res.json();
            if (res.ok) {
                showStatus(data.message || `Player ${targetName} added`, data.success);
                if (!data.success) loading = false; // Reset if player non-existent/already in list
            } else {
                throw new Error(data.detail || 'Failed to add member');
            }
        } catch (error: any) {
            console.error(error);
            showStatus(error.message || 'Connection error', false);
            loading = false;
        }
    }

    async function removeMember(name: string) {
        if (!serverOnline) return;
        loading = true;
        try {
            const res = await fetch(`/api/whitelist/members/${name}`, {
                method: 'DELETE'
            });
            const data = await res.json();
            if (res.ok) {
                showStatus(data.message || `Player ${name} removed`, data.success);
                if (!data.success) loading = false;
            } else {
                throw new Error(data.detail || 'Failed to remove member');
            }
        } catch (error: any) {
            console.error(error);
            showStatus(error.message || 'Connection error', false);
            loading = false;
        }
    }
</script>

<div class="rounded-2xl border border-slate-200 bg-indigo-50/20 p-6 shadow-sm backdrop-blur-sm transition-all dark:border-slate-800 dark:bg-indigo-900/10 group/tile flex flex-col h-full">
    <div class="flex flex-col flex-1">
        <div class="flex items-center justify-between mb-6">
            <div>
                <h2 class="text-lg font-semibold text-slate-900 dark:text-white">Whitelist</h2>
                <p class="text-xs text-slate-500 dark:text-slate-400 mt-0.5">Manage server access</p>
            </div>
            
            <div class="flex items-center gap-3">
                <span class="text-xs font-medium text-slate-500 dark:text-slate-400">
                    {whitelist.enabled ? 'Enabled' : 'Disabled'}
                </span>
                <button 
                    onclick={toggleWhitelist}
                    disabled={!serverOnline || loading}
                    class="relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed
                    {whitelist.enabled ? 'bg-green-500' : 'bg-slate-200 dark:bg-slate-700'}"
                    aria-label="Toggle Whitelist Enforcement"
                >
                    <span 
                        class="pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out
                        {whitelist.enabled ? 'translate-x-5' : 'translate-x-0'}"
                    ></span>
                </button>
            </div>
        </div>

        <!-- Add Member Form -->
        <div class="flex flex-col gap-3 mb-6">
            <div class="flex gap-2">
                <div class="relative flex-1">
                    <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                        <svg class="h-4 w-4 text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
                        </svg>
                    </div>
                    <input 
                        type="text" 
                        list="online-players-list"
                        bind:value={newMember}
                        onkeydown={(e) => e.key === 'Enter' && addMember()}
                        placeholder="Player name..."
                        disabled={!serverOnline || loading}
                        class="block w-full pl-10 pr-3 py-2 border border-slate-200 rounded-xl leading-5 bg-white dark:bg-slate-800 dark:border-slate-700 text-slate-900 dark:text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent text-sm transition-all disabled:opacity-50"
                    />
                    <datalist id="online-players-list">
                        {#each suggestions as player}
                            <option value={player.name}>Online Player</option>
                        {/each}
                    </datalist>
                </div>
                <button 
                    onclick={() => addMember()}
                    disabled={!newMember.trim() || !serverOnline || loading}
                    class="px-4 py-2 bg-green-600 hover:bg-green-700 disabled:bg-slate-300 dark:disabled:bg-slate-800 text-white rounded-xl text-sm font-semibold transition-all shadow-sm active:scale-95 flex items-center justify-center min-w-[60px]"
                >
                    Add
                </button>
            </div>

            {#if suggestions.length > 0}
                <div class="flex flex-wrap gap-2 items-center" in:fade>
                    <span class="text-[10px] uppercase tracking-wider font-bold text-slate-400 dark:text-slate-500 mr-1">Quick Add Online:</span>
                    {#each suggestions as player}
                        <button 
                            onclick={() => addMember(player.name)}
                            disabled={loading || !serverOnline}
                            class="px-2.5 py-1 text-xs rounded-full bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-green-100 dark:hover:bg-green-900/30 hover:text-green-700 dark:hover:text-green-400 transition-all border border-transparent hover:border-green-200 dark:hover:border-green-800/50 active:scale-95 disabled:opacity-50"
                        >
                            {player.name}
                        </button>
                    {/each}
                </div>
            {/if}
        </div>

        <!-- Whitelist Entries -->
        <div class="flex-1 overflow-y-auto min-h-[200px] max-h-[300px] pr-2 custom-scrollbar">
            {#if whitelist.members.length === 0}
                <div class="flex flex-col items-center justify-center h-full text-slate-400 opacity-40 py-8">
                    <svg class="h-10 w-10 mb-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                    </svg>
                    <p class="text-sm font-medium uppercase tracking-wider">No members</p>
                </div>
            {:else}
                <div class="grid grid-cols-1 gap-2">
                    {#each whitelist.members as member (member.name)}
                        <div 
                            in:fly={{ y: 20, duration: 400 }}
                            out:fade={{ duration: 200 }}
                            class="flex items-center justify-between p-3 rounded-xl bg-slate-50 dark:bg-slate-800/40 border border-slate-100 dark:border-slate-700/50 group hover:border-slate-200 dark:hover:border-slate-600 transition-all"
                        >
                            <div class="flex items-center gap-3">
                                <div class="h-8 w-8 rounded-lg overflow-hidden bg-white dark:bg-slate-700 flex items-center justify-center shadow-sm shrink-0">
                                    {#if member.avatar_url}
                                        <img 
                                            src={member.avatar_url} 
                                            alt={member.name}
                                            class="h-full w-full object-contain p-0.5"
                                            onerror={(e) => (e.currentTarget.style.display = 'none')}
                                        />
                                    {/if}
                                    <span class="text-xs font-bold text-slate-500 {member.avatar_url ? 'hidden' : ''}">{member.name[0].toUpperCase()}</span>
                                </div>
                                <span class="text-sm font-medium text-slate-700 dark:text-slate-200">{member.name}</span>
                            </div>
                            
                            <button 
                                onclick={() => removeMember(member.name)}
                                disabled={!serverOnline || loading}
                                class="p-2 text-slate-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-all opacity-0 group-hover:opacity-100 focus:opacity-100 disabled:hidden"
                                aria-label="Remove from whitelist"
                            >
                                <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                                </svg>
                            </button>
                        </div>
                    {/each}
                </div>
            {/if}
        </div>
    </div>

    {#if statusMessage}
        <div 
            transition:fly={{ y: 5, duration: 300 }}
            class="mt-4 px-4 py-2 rounded-xl text-xs font-bold ring-1 ring-inset {statusStyle} shadow-sm text-center"
        >
            {statusMessage}
        </div>
    {/if}
</div>

<style>
    .custom-scrollbar::-webkit-scrollbar {
        width: 4px;
    }
    .custom-scrollbar::-webkit-scrollbar-track {
        background: transparent;
    }
    .custom-scrollbar::-webkit-scrollbar-thumb {
        background: #cbd5e1;
        border-radius: 10px;
    }
    :global(.dark) .custom-scrollbar::-webkit-scrollbar-thumb {
        background: #334155;
    }
</style>
