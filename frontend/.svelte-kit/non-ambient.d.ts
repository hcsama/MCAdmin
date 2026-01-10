
// this file is generated — do not edit it


declare module "svelte/elements" {
	export interface HTMLAttributes<T> {
		'data-sveltekit-keepfocus'?: true | '' | 'off' | undefined | null;
		'data-sveltekit-noscroll'?: true | '' | 'off' | undefined | null;
		'data-sveltekit-preload-code'?:
			| true
			| ''
			| 'eager'
			| 'viewport'
			| 'hover'
			| 'tap'
			| 'off'
			| undefined
			| null;
		'data-sveltekit-preload-data'?: true | '' | 'hover' | 'tap' | 'off' | undefined | null;
		'data-sveltekit-reload'?: true | '' | 'off' | undefined | null;
		'data-sveltekit-replacestate'?: true | '' | 'off' | undefined | null;
	}
}

export {};


declare module "$app/types" {
	export interface AppTypes {
		RouteId(): "/" | "/api" | "/api/status-stream" | "/api/[...path]";
		RouteParams(): {
			"/api/[...path]": { path: string }
		};
		LayoutParams(): {
			"/": { path?: string };
			"/api": { path?: string };
			"/api/status-stream": Record<string, never>;
			"/api/[...path]": { path: string }
		};
		Pathname(): "/" | "/api" | "/api/" | "/api/status-stream" | "/api/status-stream/" | `/api/${string}` & {} | `/api/${string}/` & {};
		ResolvedPathname(): `${"" | `/${string}`}${ReturnType<AppTypes['Pathname']>}`;
		Asset(): "/.well-known/appspecific/com.chrome.devtools.json" | "/robots.txt" | string & {};
	}
}