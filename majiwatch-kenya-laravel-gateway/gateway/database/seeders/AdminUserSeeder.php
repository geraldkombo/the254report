<?php

namespace Database\Seeders;

use App\Models\User;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\Hash;

class AdminUserSeeder extends Seeder
{
    public function run(): void
    {
        $email = env('ADMIN_EMAIL');
        $password = env('ADMIN_BOOTSTRAP_PASSWORD');
        $stateDir = env('GATEWAY_STATE_DIR', '/state');

        if (!$email) {
            return;
        }

        $user = User::query()->where('email', $email)->first();
        if ($user) {
            if ($user->role !== 'SUPER_ADMIN') {
                $user->role = 'SUPER_ADMIN';
                $user->save();
            }
            return;
        }

        if (!$password) {
            $path = rtrim($stateDir, '/').'/admin_password';
            if (is_readable($path)) {
                $password = trim((string) file_get_contents($path));
            } else {
                $password = bin2hex(random_bytes(10));
                if (!is_dir($stateDir)) {
                    @mkdir($stateDir, 0700, true);
                }
                @file_put_contents($path, $password);
            }
        }

        User::query()->create([
            'name' => 'Admin',
            'email' => $email,
            'password' => Hash::make($password),
            'role' => 'SUPER_ADMIN',
            'email_verified_at' => now(),
        ]);
    }
}
