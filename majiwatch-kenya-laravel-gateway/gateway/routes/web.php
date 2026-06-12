<?php

use App\Http\Controllers\Admin\AdminController;
use App\Http\Controllers\ProfileController;
use Illuminate\Support\Facades\Route;

Route::get('/robots.txt', function () {
    $appUrl = rtrim(config('app.url'), '/');
    return response("User-agent: *\nAllow: /\nSitemap: {$appUrl}/sitemap.xml\n", 200)->header('Content-Type', 'text/plain');
});

Route::get('/sitemap.xml', function () {
    $appUrl = rtrim(config('app.url'), '/');
    $xml = '<?xml version="1.0" encoding="UTF-8"?>'."\n".
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'."\n".
        '  <url><loc>'.$appUrl.'/</loc></url>'."\n".
        '  <url><loc>'.$appUrl.'/login</loc></url>'."\n".
        '  <url><loc>'.$appUrl.'/register</loc></url>'."\n".
        '  <url><loc>'.$appUrl.'/app/</loc></url>'."\n".
        '</urlset>'."\n";
    return response($xml, 200)->header('Content-Type', 'application/xml');
});

Route::get('/', function () {
    $user = request()->user();
    if ($user) {
        if ($user->role === 'SUPER_ADMIN') {
            return redirect('/admin');
        }
        return redirect('/app/');
    }

    return view('portal');
});

Route::get('/dashboard', function () {
    return redirect('/app/');
})->middleware(['auth', 'verified'])->name('dashboard');

Route::get('/app', function () {
    return redirect('/app/');
});

Route::middleware(['auth', 'verified', 'role:SUPER_ADMIN'])->group(function () {
    Route::get('/admin', [AdminController::class, 'index'])->name('admin.index');
    Route::post('/admin/users/{userId}/role', [AdminController::class, 'setRole'])->name('admin.users.role');
});

Route::middleware('auth')->group(function () {
    Route::get('/profile', [ProfileController::class, 'edit'])->name('profile.edit');
    Route::patch('/profile', [ProfileController::class, 'update'])->name('profile.update');
    Route::delete('/profile', [ProfileController::class, 'destroy'])->name('profile.destroy');
});

require __DIR__.'/auth.php';
