<x-app-layout>
    <x-slot name="header">
        <div class="flex items-center justify-between gap-4 flex-wrap">
            <h2 class="font-semibold text-xl text-gray-800 leading-tight">
                {{ __('Admin Console') }}
            </h2>
            <div class="flex items-center gap-2">
                <a href="/app/" class="inline-flex items-center rounded-xl bg-gray-900 px-4 py-2 text-sm font-semibold text-white hover:bg-gray-800">
                    Open Dashboard
                </a>
            </div>
        </div>
    </x-slot>

    <div class="py-10">
        <div class="max-w-7xl mx-auto sm:px-6 lg:px-8">
            <div class="bg-white overflow-hidden shadow-sm sm:rounded-lg">
                <div class="p-6 text-gray-900">
                    <div class="text-xs tracking-[0.18em] uppercase font-semibold text-gray-500">Users</div>
                    <div class="mt-4 overflow-auto rounded-xl border border-gray-200">
                        <table class="min-w-full text-sm">
                            <thead class="bg-gray-50">
                                <tr>
                                    <th class="text-left px-4 py-3 font-semibold text-gray-700">Email</th>
                                    <th class="text-left px-4 py-3 font-semibold text-gray-700">Name</th>
                                    <th class="text-left px-4 py-3 font-semibold text-gray-700">Role</th>
                                    <th class="text-right px-4 py-3 font-semibold text-gray-700">Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                @foreach ($users as $u)
                                    <tr class="border-t border-gray-100">
                                        <td class="px-4 py-3 font-medium text-gray-900">{{ $u->email }}</td>
                                        <td class="px-4 py-3 text-gray-700">{{ $u->name }}</td>
                                        <td class="px-4 py-3">
                                            <span class="inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold {{ $u->role === 'SUPER_ADMIN' ? 'bg-emerald-100 text-emerald-800' : 'bg-gray-100 text-gray-700' }}">
                                                {{ $u->role }}
                                            </span>
                                        </td>
                                        <td class="px-4 py-3 text-right">
                                            <form method="POST" action="{{ route('admin.users.role', ['userId' => $u->id], absolute: false) }}" class="inline-flex items-center gap-2">
                                                @csrf
                                                <select name="role" class="rounded-lg border-gray-300 text-sm">
                                                    <option value="USER" @selected($u->role === 'USER')>USER</option>
                                                    <option value="SUPER_ADMIN" @selected($u->role === 'SUPER_ADMIN')>SUPER_ADMIN</option>
                                                </select>
                                                <button type="submit" class="inline-flex items-center rounded-lg bg-gray-900 px-3 py-2 text-xs font-semibold text-white hover:bg-gray-800">
                                                    Save
                                                </button>
                                            </form>
                                        </td>
                                    </tr>
                                @endforeach
                            </tbody>
                        </table>
                    </div>

                    <div class="mt-6 text-sm text-gray-600">
                        Admin email: <span class="font-semibold text-gray-900">{{ env('ADMIN_EMAIL', 'geraldshikunyi@gmail.com') }}</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
</x-app-layout>

