<script lang="ts">
    import InGameTimeCompact from './InGameTimeCompact.svelte';
    import { Copy, Check, ChevronDown, ChevronUp, Box } from 'lucide-svelte';
    import { slide, fade } from 'svelte/transition';
    
    interface ModInfo {
        id: string;
        version: string;
        file?: string;
    }

    interface Server {
        motd: string;
        online: boolean;
        version: string;
        forge_version?: string;
        mods?: ModInfo[];
        uptime?: string;
        error: string | null;
    }
    
    interface World {
        time: number;
        time_formatted: string;
        phase: string;
    }
    
    let { server, world } = $props<{ server: Server, world: World }>();

    let showMods = $state(false);
    let copied = $state(false);
    let copyTimeout: ReturnType<typeof setTimeout>;

    function handleCopyMods() {
        if (!server.mods) return;
        const modText = server.mods.map(m => `${m.id}: ${m.version}`).join('\n');
        navigator.clipboard.writeText(modText);
        copied = true;
        if (copyTimeout) clearTimeout(copyTimeout);
        copyTimeout = setTimeout(() => {
            copied = false;
        }, 2000);
    }
</script>

<div class="relative overflow-hidden rounded-2xl border border-slate-200 bg-white/50 p-4 shadow-sm backdrop-blur-md transition-all dark:border-slate-800 dark:bg-slate-900/50 mb-8">
    <div class="flex flex-col md:flex-row md:items-center justify-between gap-6">
        <!-- Server Identity & Basic Status -->
        <div class="flex items-center gap-4">
            <div class="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-slate-100 dark:bg-slate-800 shadow-inner">
                <svg class="h-7 w-7 text-slate-500 dark:text-slate-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01" />
                </svg>
            </div>
            <div class="min-w-0 flex-1">
                <div class="flex items-center gap-2">
                    <h1 class="text-xl font-bold text-slate-900 dark:text-white truncate" title={server.motd}>
                        {server.motd}
                    </h1>
                    {#if server.online}
                        <span class="flex h-2.5 w-2.5 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)] animate-pulse"></span>
                    {:else}
                        <span class="flex h-2.5 w-2.5 rounded-full bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.6)]"></span>
                    {/if}
                </div>
                <div class="flex items-center flex-wrap gap-x-2 gap-y-1 mt-0.5">
                    <span class={`text-sm font-semibold ${server.online ? 'text-green-600 dark:text-green-400' : 'text-red-500 dark:text-red-400'}`}>
                        {server.online ? 'Online' : 'Offline'}
                    </span>
                    <span class="text-slate-300 dark:text-slate-700 font-light">•</span>
                    <span class="text-sm text-slate-500 dark:text-slate-400">
                        {server.version}
                        {#if server.forge_version}
                            <span class="text-amber-600 dark:text-amber-400 font-medium ml-1">
                                (Forge {server.forge_version})
                            </span>
                        {/if}
                    </span>
                    {#if server.mods && server.mods.length > 0}
                        <span class="text-slate-300 dark:text-slate-700 font-light">•</span>
                        <button 
                            onclick={() => showMods = !showMods}
                            class="flex items-center gap-1.5 text-xs font-bold px-2 py-0.5 rounded-full bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-400 transition-colors"
                        >
                            <Box size={12} />
                            {server.mods.length} Mods
                            {#if showMods}
                                <ChevronUp size={12} />
                            {:else}
                                <ChevronDown size={12} />
                            {/if}
                        </button>
                    {/if}
                    {#if server.uptime}
                        <span class="text-slate-300 dark:text-slate-700 font-light">•</span>
                        <span class="text-sm text-slate-500 dark:text-slate-400 flex items-center gap-1">
                            <svg class="h-3.5 w-3.5 opacity-60" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            Up {server.uptime}
                        </span>
                    {/if}
                </div>
            </div>
        </div>

        <!-- In-Game Time (Pushed to the right on desktop) -->
        <div class="flex items-center gap-6 border-t border-slate-100 dark:border-slate-800 pt-4 md:border-t-0 md:pt-0">
             <div class="hidden md:block h-10 w-px bg-slate-200 dark:bg-slate-700 mx-2"></div>
             <InGameTimeCompact {server} {world} />
        </div>
    </div>
    
    {#if !server.online && server.error}
        <div class="mt-4 flex items-center gap-2 rounded-lg bg-red-50 dark:bg-red-900/20 px-3 py-2 text-sm text-red-600 dark:text-red-400">
            <svg class="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
            <span class="font-medium">{server.error}</span>
        </div>
    {/if}

    {#if showMods && server.mods && server.mods.length > 0}
        <div transition:slide class="mt-6 pt-6 border-t border-slate-100 dark:border-slate-800">
            <div class="flex items-center justify-between mb-4">
                <h3 class="text-xs font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wider flex items-center gap-2">
                    <Box size={14} />
                    Installed Mods
                </h3>
                <button 
                    onclick={handleCopyMods}
                    class="flex items-center gap-2 text-xs font-bold px-3 py-1.5 rounded-lg bg-slate-50 hover:bg-slate-100 dark:bg-slate-800 dark:hover:bg-slate-700 text-slate-600 dark:text-slate-300 transition-all active:scale-95"
                >
                    {#if copied}
                        <Check size={14} class="text-green-500" />
                        <span transition:fade={{ duration: 100 }}>Copied!</span>
                    {:else}
                        <Copy size={14} />
                        <span>Copy List</span>
                    {/if}
                </button>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2">
                {#each server.mods as mod}
                    <div 
                        class="flex flex-col gap-1 p-2 rounded-xl bg-slate-50/50 dark:bg-slate-800/30 border border-slate-100/50 dark:border-slate-800/50 group/mod"
                    >
                        <div class="flex items-center justify-between">
                            <span class="text-xs font-semibold text-slate-700 dark:text-slate-300 truncate mr-2">
                                {mod.id}
                            </span>
                            <span class="text-[10px] font-mono px-1.5 py-0.5 rounded bg-slate-200/50 dark:bg-slate-700/50 text-slate-500 dark:text-slate-400">
                                {mod.version}
                            </span>
                        </div>
                        {#if mod.file}
                            <span class="text-[9px] text-slate-400 dark:text-slate-500 truncate font-mono italic">
                                {mod.file}
                            </span>
                        {/if}
                    </div>
                {/each}
            </div>
        </div>
    {/if}
</div>
