import { Component, OnInit } from '@angular/core';
import { HttpClientModule } from '@angular/common/http';
import { BrowserModule } from '@angular/platform-browser';
import { ApiService } from './api.service';
import { FormControl, FormGroup, Validators } from '@angular/forms';

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
          console.log('Login successful:', response); /// TODO: redirect to react/some other APP
          if (response.token) {
            localStorage.setItem('authToken', response.token);
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
}
