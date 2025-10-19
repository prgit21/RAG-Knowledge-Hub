import { Component, OnInit } from '@angular/core';
import { HttpClientModule } from '@angular/common/http';
import { BrowserModule } from '@angular/platform-browser';
import { ApiService } from './api.service';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { navigateToUrl } from 'single-spa';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.sass'],
  providers: [HttpClientModule, BrowserModule, ApiService],
})
export class AppComponent implements OnInit {
  message: string = '';
  loginForm: FormGroup;

  constructor(private apiService: ApiService) {
    this.loginForm = new FormGroup({
      firstName: new FormControl('', [
        Validators.required,
        Validators.minLength(3),
      ]),
      password: new FormControl('', [
        Validators.required,
        Validators.minLength(3),
      ]),
    });
  }

  private setAuthCookie(token: string): void {
    if (typeof document === 'undefined') {
      return;
    }
    const maxAgeSeconds = 30 * 60; // Align with backend default expiry of 30 minutes.
    document.cookie = `authToken=${encodeURIComponent(token)}; Max-Age=${maxAgeSeconds}; Path=/; SameSite=Strict`;
    try {
      localStorage.setItem('authToken', token);
    } catch (error) {
      console.warn('Unable to persist auth token to localStorage.', error);
    }
  }

  ngOnInit() {
    this.apiService.getHelloMessage().subscribe(
      (data) => {
        this.message = data.message;
        console.log(this.message);
      },
      (error) => {
        console.error('Error fetching message from backend:', error);
      }
    );
  }
  onSubmit(): void {
    if (this.loginForm.valid) {
      const { firstName, password } = this.loginForm.value;

      this.apiService.postLogin(firstName, password).subscribe({
        next: (response) => {
          if (response.access_token) {
            this.setAuthCookie(response.access_token);
            navigateToUrl('/react'); // Redirect to the React parcel
          }
        },
        error: (error) => {
          console.error('Login failed:', error);
          ///TODO : Show API fail toast
        },
      });
    } else {
      console.log('Form is invalid');
      /// TODO : Show Form Invalid/dirty error
    }
  }
  getProtectedData() {
    //check if token needs to be passed from localstorage to use protected datas
    this.apiService.getProtectedData().subscribe((datum) => {
      console.log('this is protected data : ', datum);
    });
  }
}
