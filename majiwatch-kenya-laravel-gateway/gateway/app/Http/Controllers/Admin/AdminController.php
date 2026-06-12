<?php

namespace App\Http\Controllers\Admin;

use App\Http\Controllers\Controller;
use App\Models\User;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\View\View;

class AdminController extends Controller
{
    public function index(): View
    {
        $users = User::query()->orderBy('created_at', 'desc')->limit(200)->get();
        return view('admin.index', ['users' => $users]);
    }

    public function setRole(Request $request, string $userId): RedirectResponse
    {
        $request->validate([
            'role' => ['required', 'in:USER,SUPER_ADMIN'],
        ]);

        $user = User::query()->findOrFail($userId);
        if ($user->id === $request->user()->id && $request->input('role') !== 'SUPER_ADMIN') {
            return back();
        }

        $user->role = $request->input('role');
        $user->save();

        return back();
    }
}

